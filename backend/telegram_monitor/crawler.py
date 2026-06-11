"""Fetch and parse the public Telegram web message stream.

The target page is the t.me/s/<channel> preview, which renders the most recent
~20 messages as static HTML. Each message looks like:

    <div class="tgme_widget_message" data-post="Gooaye/12345" ...>
      <div class="tgme_widget_message_text">...</div>
      <a class="tgme_widget_message_date" href="https://t.me/Gooaye/12345">
        <time datetime="2026-06-11T01:00:00+00:00">...</time>
      </a>
    </div>

Older messages are paginated via ?before=<id>.

If the expected selectors stop matching (Telegram occasionally restructures the
markup) we raise StructureError loudly rather than silently returning nothing.
"""

import time
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from . import config
from .db import Post
from .logging_setup import get_logger, kv

log = get_logger("crawler")


class FetchError(RuntimeError):
    """Network/HTTP failure that survived all retries."""


class StructureError(RuntimeError):
    """Page fetched but the expected HTML structure was not found."""


def fetch_page(before: Optional[int] = None) -> str:
    """Fetch the channel page (optionally older messages via ?before=<id>).

    Retries network/5xx failures with exponential backoff (2s, 4s, 8s, ...).
    """
    url = config.channel_url()
    params = {"before": before} if before is not None else None
    headers = {
        "User-Agent": config.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    last_exc: Optional[Exception] = None
    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url, params=params, headers=headers, timeout=config.REQUEST_TIMEOUT
            )
            # Retry on transient server-side errors; fail fast on 4xx.
            if resp.status_code >= 500:
                raise FetchError(f"HTTP {resp.status_code}")
            resp.raise_for_status()
            log.info(
                "%s",
                kv(event="fetch_ok", url=resp.url, status=resp.status_code,
                   bytes=len(resp.content), attempt=attempt),
            )
            return resp.text
        except (requests.RequestException, FetchError) as exc:
            last_exc = exc
            if attempt >= config.MAX_RETRIES:
                break
            wait = config.BACKOFF_BASE ** attempt
            log.warning(
                "%s",
                kv(event="fetch_retry", url=url, attempt=attempt,
                   wait_s=wait, error=str(exc)),
            )
            time.sleep(wait)

    raise FetchError(
        f"failed to fetch {url} after {config.MAX_RETRIES} attempts: {last_exc}"
    )


def _parse_one(msg, channel: str) -> Post:
    """Parse a single tgme_widget_message div into a Post.

    Raises StructureError if mandatory fields (id, permalink, datetime) are
    missing -- those indicate a markup change we must not silently swallow.
    """
    data_post = msg.get("data-post")
    if not data_post or "/" not in data_post:
        raise StructureError(
            f"message missing/invalid data-post attribute: {data_post!r}"
        )
    try:
        post_id = int(data_post.rsplit("/", 1)[1])
    except ValueError as exc:
        raise StructureError(f"non-numeric post id in data-post={data_post!r}") from exc

    # Text is optional: media-only posts legitimately have no text node.
    text_el = msg.select_one("div.tgme_widget_message_text")
    text = text_el.get_text(separator="\n", strip=True) if text_el else ""

    date_a = msg.select_one("a.tgme_widget_message_date")
    if date_a is None or not date_a.get("href"):
        raise StructureError(
            f"post {post_id}: missing a.tgme_widget_message_date / href"
        )
    url = date_a["href"]

    time_el = date_a.select_one("time")
    posted_at = time_el.get("datetime") if time_el else None
    if not posted_at:
        raise StructureError(f"post {post_id}: missing time[datetime]")

    return Post(
        post_id=post_id,
        channel=channel,
        text=text,
        posted_at=posted_at,
        url=url,
    )


def parse_posts(html: str, channel: str) -> List[Post]:
    """Parse all messages on a page into Post objects, ascending by id.

    Raises StructureError if the page contains no message containers at all,
    which almost certainly means the selectors are out of date (or the channel
    is gone), rather than genuinely having zero posts.
    """
    soup = BeautifulSoup(html, "lxml")
    messages = soup.select("div.tgme_widget_message")
    if not messages:
        raise StructureError(
            "no 'div.tgme_widget_message' elements found -- selector likely "
            "changed or the page was not the expected channel stream"
        )

    posts = [_parse_one(msg, channel) for msg in messages]
    posts.sort(key=lambda p: p.post_id)
    log.info("%s", kv(event="parse_ok", count=len(posts),
                      min_id=posts[0].post_id, max_id=posts[-1].post_id))
    return posts
