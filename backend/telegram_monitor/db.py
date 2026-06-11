"""SQLite persistence for crawled Telegram posts.

Adds a single isolated table (telegram_posts) to the existing market_data.db.
Existing tables are never read or modified.
"""

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List

from . import config
from .logging_setup import get_logger, kv

log = get_logger("db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS telegram_posts (
    post_id    INTEGER PRIMARY KEY,   -- numeric id from data-post="<channel>/<id>"
    channel    TEXT NOT NULL,         -- e.g. 'Gooaye'
    text       TEXT,                  -- message text (may be empty for media-only)
    posted_at  TEXT,                  -- ISO8601 from time[datetime]
    url        TEXT,                  -- permalink to the post
    fetched_at TEXT NOT NULL,         -- when we crawled it (ISO8601 UTC)
    notified   INTEGER NOT NULL DEFAULT 0  -- flag for the Discord push hook
);
"""


@dataclass
class Post:
    """A single parsed Telegram post."""

    post_id: int
    channel: str
    text: str
    posted_at: str
    url: str

    def summary(self, n: int) -> str:
        flat = " ".join((self.text or "").split())
        return flat[:n]


@contextmanager
def connect(db_path: str = None) -> Iterator[sqlite3.Connection]:
    """Open a connection, ensuring the parent directory and schema exist."""
    path = db_path or config.DB_PATH
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.row_factory = sqlite3.Row
        init_schema(conn)
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def get_max_post_id(conn: sqlite3.Connection, channel: str) -> int:
    """Largest stored post_id for the channel; 0 if the channel has no rows."""
    row = conn.execute(
        "SELECT MAX(post_id) AS max_id FROM telegram_posts WHERE channel = ?",
        (channel,),
    ).fetchone()
    return int(row["max_id"]) if row and row["max_id"] is not None else 0


def get_min_post_id(conn: sqlite3.Connection, channel: str) -> int:
    """Smallest stored post_id for the channel; 0 if the channel has no rows."""
    row = conn.execute(
        "SELECT MIN(post_id) AS min_id FROM telegram_posts WHERE channel = ?",
        (channel,),
    ).fetchone()
    return int(row["min_id"]) if row and row["min_id"] is not None else 0


def insert_posts(
    conn: sqlite3.Connection, posts: Iterable[Post], fetched_at: str
) -> List[Post]:
    """INSERT OR IGNORE the given posts (ascending by id recommended).

    Returns the posts that were actually inserted (i.e. not already present),
    so callers can drive notifications off genuinely-new rows.
    """
    posts = list(posts)
    inserted: List[Post] = []
    for post in posts:
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO telegram_posts
                (post_id, channel, text, posted_at, url, fetched_at, notified)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (
                post.post_id,
                post.channel,
                post.text,
                post.posted_at,
                post.url,
                fetched_at,
            ),
        )
        if cur.rowcount > 0:
            inserted.append(post)
    log.debug("%s", kv(event="insert_posts", attempted=len(posts), inserted=len(inserted)))
    return inserted


def mark_notified(conn: sqlite3.Connection, post_ids: Iterable[int]) -> int:
    """Set notified=1 for the given post ids. Returns rows updated.

    Used by the Discord push hook after a successful push.
    """
    ids = list(post_ids)
    if not ids:
        return 0
    placeholders = ",".join("?" for _ in ids)
    cur = conn.execute(
        f"UPDATE telegram_posts SET notified = 1 WHERE post_id IN ({placeholders})",
        ids,
    )
    return cur.rowcount
