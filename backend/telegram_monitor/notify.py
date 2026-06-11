"""Pluggable notification hook (placeholder).

This is intentionally a no-op for the MVP. The crawler calls notify(posts)
after persisting genuinely-new posts so that a future LINE push integration
(Flask webhook + gemini-2.5-flash summary) can be dropped in here without
touching the crawl/store pipeline.

Contract for a real implementation:
  - Receive the list of newly-inserted Post objects (ascending by id).
  - Push them (e.g. to a LINE channel), generating summaries as needed.
  - On successful push, mark the posts as notified so they are not re-sent:

        from .db import connect, mark_notified
        with connect() as conn:
            mark_notified(conn, [p.post_id for p in pushed])

  - Failures should be raised/logged, NOT silently swallowed, so the next
    cron run can retry the un-notified rows.
"""

from typing import List

from .db import Post
from .logging_setup import get_logger, kv

log = get_logger("notify")


def notify(posts: List[Post]) -> None:
    """No-op hook. Logs that posts are pending notification.

    Replace the body with the LINE push implementation. Until then, new posts
    simply remain with notified=0 in the DB.
    """
    if not posts:
        return
    log.info(
        "%s",
        kv(event="notify_pending", count=len(posts),
           ids=",".join(str(p.post_id) for p in posts)),
    )
    # Intentionally not marking notified: no real push happened yet.
