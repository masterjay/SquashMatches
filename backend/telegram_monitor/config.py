"""Configuration for the Telegram channel monitor.

All knobs are overridable via environment variables so the same module can run
unchanged on a GCP VM cron job, in a container, or on a developer laptop.
"""

import os
from pathlib import Path

# --- Paths -----------------------------------------------------------------

# Repo root is two levels up from this file: <root>/backend/telegram_monitor/.
_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent.parent

# Existing shared SQLite DB. A new, isolated table is added here; existing
# tables are never touched.
DB_PATH = os.environ.get(
    "TELEGRAM_MONITOR_DB_PATH",
    str(_REPO_ROOT / "backend" / "data" / "market_data.db"),
)

# --- Source ----------------------------------------------------------------

# Channel username (the part after t.me/s/). data-post is "<CHANNEL>/<id>".
CHANNEL = os.environ.get("TELEGRAM_MONITOR_CHANNEL", "Gooaye")

# Public web preview base. Final URL is BASE_URL + CHANNEL.
BASE_URL = os.environ.get("TELEGRAM_MONITOR_BASE_URL", "https://t.me/s/")

# A normal browser User-Agent. t.me serves the preview page only to clients
# that look like real browsers.
USER_AGENT = os.environ.get(
    "TELEGRAM_MONITOR_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
)

# --- Polite crawling -------------------------------------------------------

# Seconds to wait for each HTTP request.
REQUEST_TIMEOUT = float(os.environ.get("TELEGRAM_MONITOR_TIMEOUT", "15"))

# Exponential backoff retry on network failures: 2s, 4s, 8s, ... up to
# MAX_RETRIES attempts.
MAX_RETRIES = int(os.environ.get("TELEGRAM_MONITOR_MAX_RETRIES", "4"))
BACKOFF_BASE = float(os.environ.get("TELEGRAM_MONITOR_BACKOFF_BASE", "2"))

# Pause between pages while back-filling, to avoid hammering t.me.
BACKFILL_PAGE_DELAY = float(os.environ.get("TELEGRAM_MONITOR_BACKFILL_DELAY", "1.5"))

# Safety cap on how many pages a single backfill run will walk back.
BACKFILL_MAX_PAGES = int(os.environ.get("TELEGRAM_MONITOR_BACKFILL_MAX_PAGES", "50"))

# Informational only: recommended cron interval in minutes. The cron scheduler
# (not this process) actually enforces the polling cadence.
POLL_INTERVAL_MINUTES = int(os.environ.get("TELEGRAM_MONITOR_INTERVAL_MIN", "30"))

# Number of characters used for the summary in logs / new-post listing.
SUMMARY_CHARS = int(os.environ.get("TELEGRAM_MONITOR_SUMMARY_CHARS", "80"))

# --- Discord push ----------------------------------------------------------

# Incoming webhook URL for the Discord channel to push new posts to. This is a
# secret -- set it via the environment, do NOT commit it. If empty, the notify
# hook is skipped and posts remain notified=0 for a later retry.
DISCORD_WEBHOOK_URL = os.environ.get("TELEGRAM_MONITOR_DISCORD_WEBHOOK", "")


def channel_url() -> str:
    """Full URL of the channel's public web message stream."""
    return f"{BASE_URL}{CHANNEL}"
