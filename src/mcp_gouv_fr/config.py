"""Shared configuration for all mounted APIs (HTTP client defaults)."""

from __future__ import annotations

import logging
import os

_log = logging.getLogger(__name__)

HTTP_TIMEOUT_S = float(os.environ.get("MCP_GOUV_HTTP_TIMEOUT", "30"))

HTTP_USER_AGENT = os.environ.get(
    "MCP_GOUV_USER_AGENT",
    "mcp-gouv-fr/0.1 (+https://github.com/gghez/mcp-gouv-fr)",
)

_log.info("config: HTTP_TIMEOUT_S=%s", HTTP_TIMEOUT_S)
_log.info("config: HTTP_USER_AGENT=%s", HTTP_USER_AGENT)
