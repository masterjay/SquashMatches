"""Structured logging helper.

Emits single-line, key=value style records that are easy to grep in cron logs
and to ingest into log pipelines. All message prefixes are pure ASCII tags
(e.g. [Crawl], [DB]) per project convention -- no emoji.
"""

import logging
import sys

_CONFIGURED = False


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger once, writing to stderr."""
    global _CONFIGURED
    if _CONFIGURED:
        return
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    root = logging.getLogger("telegram_monitor")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers[:] = [handler]
    root.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"telegram_monitor.{name}")


def kv(**fields) -> str:
    """Render fields as a structured key=value string.

    Values containing spaces are quoted so the line stays parseable.
    """
    parts = []
    for key, value in fields.items():
        text = str(value)
        if " " in text or "=" in text:
            text = '"' + text.replace('"', '\\"') + '"'
        parts.append(f"{key}={text}")
    return " ".join(parts)
