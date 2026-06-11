"""Offline tests for parsing + dedup logic.

These do not hit the network. They feed representative t.me/s/ markup into the
parser and exercise the SQLite dedup / new-post selection directly, covering
the acceptance criteria:
  - first run inserts everything, no duplicates
  - second run (no new posts) inserts nothing and does not error
  - lowering last_seen surfaces "new" posts again

Run:  python -m backend.telegram_monitor.test_telegram_monitor
"""

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from . import config, notify
from .crawler import StructureError, parse_posts
from .db import (
    Post,
    connect,
    get_max_post_id,
    insert_posts,
)


def _msg(pid, text="hello world", dt="2026-06-11T01:00:00+00:00"):
    return f"""
    <div class="tgme_widget_message_wrap">
      <div class="tgme_widget_message" data-post="Gooaye/{pid}">
        <div class="tgme_widget_message_text">{text}</div>
        <div class="tgme_widget_message_footer">
          <a class="tgme_widget_message_date" href="https://t.me/Gooaye/{pid}">
            <time datetime="{dt}">01:00</time>
          </a>
        </div>
      </div>
    </div>
    """


def _page(ids):
    body = "\n".join(_msg(i, text=f"post number {i}") for i in ids)
    return f"<html><body>{body}</body></html>"


class ParseTests(unittest.TestCase):
    def test_parse_basic(self):
        posts = parse_posts(_page([10, 11, 12]), "Gooaye")
        self.assertEqual([p.post_id for p in posts], [10, 11, 12])  # sorted asc
        self.assertEqual(posts[0].channel, "Gooaye")
        self.assertEqual(posts[0].url, "https://t.me/Gooaye/10")
        self.assertEqual(posts[0].posted_at, "2026-06-11T01:00:00+00:00")
        self.assertEqual(posts[0].text, "post number 10")

    def test_media_only_post_has_empty_text(self):
        html = """
        <div class="tgme_widget_message" data-post="Gooaye/99">
          <a class="tgme_widget_message_date" href="https://t.me/Gooaye/99">
            <time datetime="2026-06-11T02:00:00+00:00">02:00</time>
          </a>
        </div>
        """
        posts = parse_posts(html, "Gooaye")
        self.assertEqual(posts[0].text, "")

    def test_no_messages_raises(self):
        with self.assertRaises(StructureError):
            parse_posts("<html><body>nothing here</body></html>", "Gooaye")

    def test_missing_datetime_raises(self):
        html = """
        <div class="tgme_widget_message" data-post="Gooaye/5">
          <div class="tgme_widget_message_text">x</div>
          <a class="tgme_widget_message_date" href="https://t.me/Gooaye/5"></a>
        </div>
        """
        with self.assertRaises(StructureError):
            parse_posts(html, "Gooaye")


class DedupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "test.db")

    def tearDown(self):
        self.tmp.cleanup()

    def _now(self):
        return datetime.now(timezone.utc).isoformat()

    def _poll(self, ids, forced_last_seen=None):
        """Mimic process_new_posts against an in-memory page."""
        posts = parse_posts(_page(ids), "Gooaye")
        with connect(self.db) as conn:
            last_seen = (
                forced_last_seen
                if forced_last_seen is not None
                else get_max_post_id(conn, "Gooaye")
            )
            new = [p for p in posts if p.post_id > last_seen]
            new.sort(key=lambda p: p.post_id)
            inserted = insert_posts(conn, new, self._now())
        return inserted

    def test_first_run_inserts_all(self):
        inserted = self._poll([10, 11, 12])
        self.assertEqual([p.post_id for p in inserted], [10, 11, 12])

    def test_second_run_no_new(self):
        self._poll([10, 11, 12])
        inserted = self._poll([10, 11, 12])  # same page, nothing new
        self.assertEqual(inserted, [])

    def test_new_post_appears(self):
        self._poll([10, 11, 12])
        inserted = self._poll([10, 11, 12, 13])
        self.assertEqual([p.post_id for p in inserted], [13])

    def test_forced_lower_last_seen_resurfaces(self):
        self._poll([10, 11, 12])
        # Pretend we only saw up to 10 -> 11 and 12 are "new" again, but
        # INSERT OR IGNORE means no duplicate rows are created.
        inserted = self._poll([10, 11, 12], forced_last_seen=10)
        self.assertEqual([p.post_id for p in inserted], [])  # already stored

    def test_no_duplicate_rows(self):
        self._poll([10, 11, 12])
        self._poll([10, 11, 12])
        with connect(self.db) as conn:
            count = conn.execute(
                "SELECT COUNT(*) AS c FROM telegram_posts"
            ).fetchone()["c"]
        self.assertEqual(count, 3)


class _FakeResp:
    def __init__(self, status_code=204, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"HTTP {self.status_code}")


class NotifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "test.db")
        self._orig_db = config.DB_PATH
        self._orig_hook = config.DISCORD_WEBHOOK_URL
        config.DB_PATH = self.db
        config.DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1/abc"
        # Seed two stored posts (notified=0) to push.
        self.posts = [
            Post(201, "Gooaye", "first", "2026-06-11T01:00:00+00:00", "https://t.me/Gooaye/201"),
            Post(202, "Gooaye", "second", "2026-06-11T02:00:00+00:00", "https://t.me/Gooaye/202"),
        ]
        with connect(self.db) as conn:
            insert_posts(conn, self.posts, datetime.now(timezone.utc).isoformat())

    def tearDown(self):
        config.DB_PATH = self._orig_db
        config.DISCORD_WEBHOOK_URL = self._orig_hook
        self.tmp.cleanup()

    def _notified_flags(self):
        with connect(self.db) as conn:
            rows = conn.execute(
                "SELECT post_id, notified FROM telegram_posts ORDER BY post_id"
            ).fetchall()
        return {r["post_id"]: r["notified"] for r in rows}

    def test_build_payload_shape(self):
        payload = notify._build_payload(self.posts[0])
        embed = payload["embeds"][0]
        self.assertEqual(embed["title"], "Gooaye #201")
        self.assertEqual(embed["url"], "https://t.me/Gooaye/201")
        self.assertEqual(embed["timestamp"], "2026-06-11T01:00:00+00:00")
        self.assertEqual(embed["description"], "first")

    def test_success_marks_notified(self):
        with mock.patch.object(notify.requests, "post", return_value=_FakeResp(204)) as p:
            sent = notify.notify(self.posts)
        self.assertEqual(sent, [201, 202])
        self.assertEqual(p.call_count, 2)
        self.assertEqual(self._notified_flags(), {201: 1, 202: 1})

    def test_skips_when_no_webhook(self):
        config.DISCORD_WEBHOOK_URL = ""
        with mock.patch.object(notify.requests, "post") as p:
            sent = notify.notify(self.posts)
        self.assertEqual(sent, [])
        p.assert_not_called()
        self.assertEqual(self._notified_flags(), {201: 0, 202: 0})

    def test_failure_leaves_remaining_unnotified(self):
        # First post fails permanently -> nothing notified, run aborts.
        with mock.patch.object(notify.requests, "post", return_value=_FakeResp(500)):
            with mock.patch.object(notify.time, "sleep"):  # no real backoff wait
                sent = notify.notify(self.posts)
        self.assertEqual(sent, [])
        self.assertEqual(self._notified_flags(), {201: 0, 202: 0})


if __name__ == "__main__":
    unittest.main(verbosity=2)
