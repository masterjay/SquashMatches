"""CLI entry point.

Default: a single poll (suitable for cron). --backfill walks history backward.

Usage:
  python -m backend.telegram_monitor                 # one poll
  python -m backend.telegram_monitor --backfill      # backfill from oldest stored
  python -m backend.telegram_monitor --backfill --before 12345 --max-pages 10
"""

import argparse
import sys

from . import config
from .crawler import FetchError, StructureError
from .logging_setup import get_logger, setup_logging
from .monitor import backfill, process_new_posts

log = get_logger("cli")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="telegram_monitor",
        description="Poll a public Telegram channel and store new posts.",
    )
    parser.add_argument(
        "--backfill",
        action="store_true",
        help="Walk older pages (?before=<id>) to recover missed posts.",
    )
    parser.add_argument(
        "--before",
        type=int,
        default=None,
        help="Backfill starting point (post id). Defaults to oldest stored id.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help=f"Max pages to walk during backfill (default {config.BACKFILL_MAX_PAGES}).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ...). Default INFO.",
    )
    args = parser.parse_args(argv)

    setup_logging(args.log_level)

    try:
        if args.backfill:
            new = backfill(before=args.before, max_pages=args.max_pages)
        else:
            new = process_new_posts()
    except StructureError as exc:
        log.error("structure error: %s", exc)
        return 2
    except FetchError as exc:
        log.error("fetch error: %s", exc)
        return 3

    # Concise human-facing summary in addition to structured logs.
    print(f"channel={config.CHANNEL} new_posts={len(new)}")
    for p in new:
        print(f"  [{p.post_id}] {p.posted_at} {p.summary(config.SUMMARY_CHARS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
