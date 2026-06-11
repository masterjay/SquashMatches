"""Orchestration: poll once, or backfill history.

Pipeline (run_once):
  1. read current max post_id from DB as last_seen
  2. fetch + parse the channel page
  3. keep only post_id > last_seen, ascending
  4. INSERT OR IGNORE, collect genuinely-new rows
  5. structured-log the new posts (id, time, first N chars)
  6. call the pluggable notify() hook
"""

import time
from datetime import datetime, timezone
from typing import List

from . import config
from .crawler import fetch_page, parse_posts
from .db import Post, connect, get_max_post_id, get_min_post_id, insert_posts
from .logging_setup import get_logger, kv
from .notify import notify

log = get_logger("monitor")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log_new_posts(new_posts: List[Post]) -> None:
    for p in new_posts:
        log.info(
            "%s",
            kv(event="new_post", id=p.post_id, posted_at=p.posted_at,
               url=p.url, summary=p.summary(config.SUMMARY_CHARS)),
        )


def process_new_posts(channel: str = None) -> List[Post]:
    """Single poll. Returns the list of newly-inserted posts (may be empty)."""
    channel = channel or config.CHANNEL
    fetched_at = _utc_now_iso()

    with connect() as conn:
        last_seen = get_max_post_id(conn, channel)
        log.info("%s", kv(event="poll_start", channel=channel, last_seen=last_seen))

        html = fetch_page()
        posts = parse_posts(html, channel)

        new_posts = [p for p in posts if p.post_id > last_seen]
        new_posts.sort(key=lambda p: p.post_id)

        inserted = insert_posts(conn, new_posts, fetched_at)

    log.info(
        "%s",
        kv(event="poll_done", channel=channel, fetched=len(posts),
           new=len(inserted), last_seen=last_seen),
    )
    _log_new_posts(inserted)

    # Pluggable downstream hook (Discord webhook push).
    notify(inserted)
    return inserted


def backfill(before: int = None, max_pages: int = None) -> List[Post]:
    """Walk older pages via ?before=<id> to recover posts missed while down.

    Starts just below the oldest stored post (or an explicit --before id),
    inserts anything new, and stops when a page yields no new rows, returns no
    messages, or the page cap is reached. Dedup is handled by INSERT OR IGNORE.
    """
    channel = config.CHANNEL
    max_pages = max_pages or config.BACKFILL_MAX_PAGES
    fetched_at = _utc_now_iso()

    with connect() as conn:
        if before is None:
            min_id = get_min_post_id(conn, channel)
            before = min_id if min_id > 0 else None
        log.info("%s", kv(event="backfill_start", channel=channel,
                          before=before, max_pages=max_pages))

        all_inserted: List[Post] = []
        cursor = before
        for page in range(1, max_pages + 1):
            html = fetch_page(before=cursor)
            posts = parse_posts(html, channel)
            if not posts:
                log.info("%s", kv(event="backfill_empty_page", page=page))
                break

            inserted = insert_posts(conn, posts, fetched_at)
            all_inserted.extend(inserted)
            log.info("%s", kv(event="backfill_page", page=page,
                              fetched=len(posts), new=len(inserted),
                              min_id=posts[0].post_id))

            if not inserted:
                # Everything on this page is already stored -> caught up.
                log.info("%s", kv(event="backfill_caught_up", page=page))
                break

            # Page back from the oldest id we just saw.
            cursor = posts[0].post_id
            time.sleep(config.BACKFILL_PAGE_DELAY)

    log.info("%s", kv(event="backfill_done", channel=channel,
                      new=len(all_inserted)))
    _log_new_posts(all_inserted)
    notify(all_inserted)
    return all_inserted
