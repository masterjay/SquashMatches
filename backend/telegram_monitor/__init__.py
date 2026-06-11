"""Telegram public-channel polling crawler (MVP: fetch + store).

Fetches new posts from the t.me/s/<channel> web stream, dedupes via SQLite,
and pushes new posts to a Discord channel via the notify() webhook hook.
"""

from .db import Post
from .monitor import backfill, process_new_posts

__all__ = ["Post", "process_new_posts", "backfill"]
