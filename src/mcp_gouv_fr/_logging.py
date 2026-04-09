"""Central logging setup (call once from CLI before other package imports run servers)."""

from __future__ import annotations

import logging
import os
import sys


def configure_logging() -> None:
    """Configure root logging for stderr (safe with MCP stdio transport).

    Level from env ``MCP_GOUV_LOG_LEVEL`` (default ``INFO``).
    """
    level_name = os.environ.get("MCP_GOUV_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, None)
    warn_invalid = False
    if not isinstance(level, int):
        level = logging.INFO
        warn_invalid = True

    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        root.addHandler(handler)
    root.setLevel(level)

    if warn_invalid:
        logging.getLogger(__name__).warning(
            "Invalid MCP_GOUV_LOG_LEVEL=%r, using INFO",
            level_name,
        )
