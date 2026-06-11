# Telegram Channel Monitor (`telegram_monitor`)

Polling crawler for the public Telegram channel **股癌 Gooaye**
(<https://t.me/s/Gooaye>). It fetches the latest posts from the public web
message stream, dedupes them in SQLite, and only processes posts it has not
seen before. New posts are pushed to a **Discord channel** via an incoming
webhook (the pluggable `notify()` hook).

## What it does

1. Reads the current max `post_id` from the DB as `last_seen`.
2. Fetches `https://t.me/s/Gooaye` with a normal browser User-Agent
   (`requests` + `BeautifulSoup(lxml)`).
3. Parses every `div.tgme_widget_message`:
   - `post_id` from `data-post="Gooaye/<id>"`
   - text from `div.tgme_widget_message_text`
   - `posted_at` from `time[datetime]`
   - `url` from `a.tgme_widget_message_date[href]`
4. Keeps only `post_id > last_seen`, ascending, and `INSERT OR IGNORE`s them.
5. Emits a structured log line per new post (id, time, first 80 chars) and
   pushes each new post to Discord via `notify(posts)`. Successfully-pushed
   posts are flagged `notified=1`; failures stay `notified=0` for the next run.

If the expected selectors stop matching (Telegram occasionally restructures the
markup), the crawler raises `StructureError` **loudly** rather than silently
returning nothing. Network/5xx failures are retried with exponential backoff.

> **Note on selectors:** the build environment for this change could not reach
> `t.me` (HTTP 403 from the datacenter network), so selectors were implemented
> against the documented, long-stable `t.me/s/` markup and covered by offline
> fixture tests. Run the manual smoke test below from the GCP VM once to confirm
> the live page still matches before wiring up cron.

## Data table

Added to the existing `backend/data/market_data.db`, isolated from other tables:

```
telegram_posts(
  post_id    INTEGER PRIMARY KEY,   -- numeric id from data-post
  channel    TEXT,                  -- 'Gooaye'
  text       TEXT,
  posted_at  TEXT,                  -- ISO8601 from time[datetime]
  url        TEXT,
  fetched_at TEXT,                  -- crawl time (ISO8601 UTC)
  notified   INTEGER DEFAULT 0      -- flag for the Discord push hook
)
```

## Install

```bash
pip install -r backend/telegram_monitor/requirements.txt
```

## Run

Run from the **repository root** so the `backend.telegram_monitor` package
resolves.

Single poll (default; this is what cron runs):

```bash
python -m backend.telegram_monitor
```

Backfill history (recover posts missed while the machine was down). Walks older
pages via `?before=<id>`, stopping when it reaches posts already stored:

```bash
# from the oldest post currently in the DB
python -m backend.telegram_monitor --backfill

# from a specific id, capped at 10 pages
python -m backend.telegram_monitor --backfill --before 12345 --max-pages 10
```

Verbose logging:

```bash
python -m backend.telegram_monitor --log-level DEBUG
```

Exit codes: `0` success, `2` HTML structure error (selectors changed),
`3` fetch error (network exhausted retries).

## Manual test / acceptance

```bash
# 1. First run: stores all currently-visible posts, no duplicates.
python -m backend.telegram_monitor

# 2. Second run (no new posts): prints new_posts=0, no error.
python -m backend.telegram_monitor

# 3. Force a smaller last_seen to prove "new" detection works.
sqlite3 backend/data/market_data.db \
  "DELETE FROM telegram_posts WHERE post_id > (SELECT MIN(post_id) FROM telegram_posts);"
python -m backend.telegram_monitor   # the deleted ids are re-detected and re-stored
```

Offline unit tests (no network needed):

```bash
python -m backend.telegram_monitor.test_telegram_monitor
```

## Cron (recommended: every 30 minutes)

On the GCP VM, edit the crontab (`crontab -e`). Adjust the repo path and Python
interpreter to match your deployment:

```cron
# Poll Gooaye every 30 minutes; append logs for debugging.
# Set the Discord webhook here (or in a sourced env file) so cron sees it.
*/30 * * * * cd /opt/MyStock && TELEGRAM_MONITOR_DISCORD_WEBHOOK='https://discord.com/api/webhooks/XXX/YYY' /usr/bin/python3 -m backend.telegram_monitor >> /var/log/telegram_monitor.log 2>&1
```

If you use a virtualenv, point at its interpreter, e.g.
`/opt/MyStock/.venv/bin/python -m backend.telegram_monitor`.

## Configuration

All settings are environment variables with sensible defaults (see
`config.py`):

| Variable | Default | Purpose |
| --- | --- | --- |
| `TELEGRAM_MONITOR_DB_PATH` | `backend/data/market_data.db` | SQLite DB path |
| `TELEGRAM_MONITOR_CHANNEL` | `Gooaye` | Channel username |
| `TELEGRAM_MONITOR_BASE_URL` | `https://t.me/s/` | Web stream base URL |
| `TELEGRAM_MONITOR_USER_AGENT` | a Chrome UA | Request User-Agent |
| `TELEGRAM_MONITOR_TIMEOUT` | `15` | Per-request timeout (s) |
| `TELEGRAM_MONITOR_MAX_RETRIES` | `4` | Retry attempts on failure |
| `TELEGRAM_MONITOR_BACKOFF_BASE` | `2` | Backoff base (2s, 4s, 8s, ...) |
| `TELEGRAM_MONITOR_BACKFILL_DELAY` | `1.5` | Delay between backfill pages (s) |
| `TELEGRAM_MONITOR_BACKFILL_MAX_PAGES` | `50` | Backfill page cap |
| `TELEGRAM_MONITOR_INTERVAL_MIN` | `30` | Informational cron cadence |
| `TELEGRAM_MONITOR_SUMMARY_CHARS` | `80` | Summary length in logs |
| `TELEGRAM_MONITOR_DISCORD_WEBHOOK` | _(empty)_ | Discord webhook URL (secret) |

## Discord push

New posts are pushed to a Discord channel via an **incoming webhook**. Each post
is sent as an embed (title `Gooaye #<id>` linking to the post, the post text as
the description, and the post timestamp).

Configure the webhook via the environment -- it is a secret, so it is **not**
committed to the repo:

```bash
export TELEGRAM_MONITOR_DISCORD_WEBHOOK='https://discord.com/api/webhooks/<id>/<token>'
python -m backend.telegram_monitor
```

Behaviour:

- Posts are sent oldest-first so they read chronologically in the channel.
- On a successful push, the row is flagged `notified=1` and is never re-sent.
- On failure (network, 5xx, rate limit exhausted), the post stays `notified=0`
  and the run stops sending so order is preserved; the next cron run retries it.
- Discord `429` rate limits are honoured via `retry_after`.
- If the webhook env var is unset, pushing is skipped with a warning and posts
  remain `notified=0` (crawl + store still works).

To preview the exact payload without hitting Discord:

```bash
python - <<'PY'
import os
os.environ.setdefault("TELEGRAM_MONITOR_DISCORD_WEBHOOK", "x")
from backend.telegram_monitor.db import Post
from backend.telegram_monitor.notify import _build_payload
import json
print(json.dumps(_build_payload(Post(123, "Gooaye", "hello", "2026-06-11T01:00:00+00:00", "https://t.me/Gooaye/123")), ensure_ascii=False, indent=2))
PY
```

## Layout

```
backend/telegram_monitor/
  __init__.py        # package exports
  __main__.py        # CLI entry (python -m backend.telegram_monitor)
  config.py          # env-driven configuration
  logging_setup.py   # structured key=value logging
  db.py              # SQLite schema + helpers, Post dataclass
  crawler.py         # fetch (retry/backoff) + parse (StructureError)
  monitor.py         # process_new_posts(), backfill()
  notify.py          # Discord webhook push (notify hook)
  requirements.txt
  test_telegram_monitor.py
  README.md
```
