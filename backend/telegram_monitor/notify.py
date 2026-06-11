"""Discord webhook notification hook.

After the crawler persists genuinely-new posts it calls notify(posts), which
pushes each post to a Discord channel via an incoming webhook. On a successful
push the post is marked notified=1 so it is not re-sent; failures are logged and
left with notified=0 so the next cron run retries them.

The webhook URL is a secret and is read from the environment
(TELEGRAM_MONITOR_DISCORD_WEBHOOK). If it is unset, notification is skipped with
a warning and posts remain notified=0.
"""

import time
from typing import List

import requests

from . import config
from .db import Post, connect, mark_notified
from .logging_setup import get_logger, kv

log = get_logger("notify")

# Discord embed description hard limit is 4096 chars; keep margin.
_MAX_DESC = 3800


def _build_payload(post: Post) -> dict:
    """Build a Discord webhook JSON payload (single embed) for one post."""
    text = post.text or "(no text / media post)"
    if len(text) > _MAX_DESC:
        text = text[:_MAX_DESC] + "\n..."
    return {
        "embeds": [
            {
                "title": f"{config.CHANNEL} #{post.post_id}",
                "url": post.url,
                "description": text,
                "timestamp": post.posted_at,  # ISO8601 from time[datetime]
                "footer": {"text": config.CHANNEL},
            }
        ]
    }


def _post_to_discord(webhook_url: str, payload: dict) -> bool:
    """POST a single payload to Discord, honoring 429 rate limits and 5xx.

    Returns True on success (HTTP 2xx). Retries transient failures with
    exponential backoff; returns False once attempts are exhausted.
    """
    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            resp = requests.post(
                webhook_url, json=payload, timeout=config.REQUEST_TIMEOUT
            )
            if resp.status_code == 429:
                # Rate limited: respect Discord's retry_after if present.
                retry_after = config.BACKOFF_BASE ** attempt
                try:
                    retry_after = float(resp.json().get("retry_after", retry_after))
                except ValueError:
                    pass
                log.warning("%s", kv(event="discord_rate_limited",
                                     attempt=attempt, wait_s=retry_after))
                time.sleep(retry_after)
                continue
            if resp.status_code >= 500:
                raise requests.RequestException(f"HTTP {resp.status_code}")
            resp.raise_for_status()
            return True
        except requests.RequestException as exc:
            if attempt >= config.MAX_RETRIES:
                log.error("%s", kv(event="discord_failed", attempt=attempt,
                                   error=str(exc)))
                return False
            wait = config.BACKOFF_BASE ** attempt
            log.warning("%s", kv(event="discord_retry", attempt=attempt,
                                 wait_s=wait, error=str(exc)))
            time.sleep(wait)
    return False


def notify(posts: List[Post]) -> List[int]:
    """Push new posts to Discord. Returns the ids successfully notified.

    Posts are sent oldest-first so they read chronologically in the channel.
    Each successful push flips notified=1 in the DB.
    """
    if not posts:
        return []

    webhook_url = config.DISCORD_WEBHOOK_URL
    if not webhook_url:
        log.warning(
            "%s",
            kv(event="notify_skipped", reason="no_webhook_configured",
               count=len(posts)),
        )
        return []

    ordered = sorted(posts, key=lambda p: p.post_id)
    sent_ids: List[int] = []
    for post in ordered:
        if _post_to_discord(webhook_url, _build_payload(post)):
            sent_ids.append(post.post_id)
            log.info("%s", kv(event="discord_sent", id=post.post_id))
        else:
            # Stop on first hard failure: leave this and the rest as notified=0
            # so ordering is preserved on the next run's retry.
            log.error("%s", kv(event="notify_aborted", id=post.post_id,
                               remaining=len(ordered) - len(sent_ids)))
            break

    if sent_ids:
        with connect() as conn:
            mark_notified(conn, sent_ids)
        log.info("%s", kv(event="notify_done", notified=len(sent_ids)))
    return sent_ids
