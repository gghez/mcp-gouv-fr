"""Shared configuration for all mounted APIs (HTTP client defaults)."""

from __future__ import annotations

import os

HTTP_TIMEOUT_S = float(os.environ.get("MCP_GOUV_HTTP_TIMEOUT", "30"))

HTTP_USER_AGENT = os.environ.get(
    "MCP_GOUV_USER_AGENT",
    "mcp-gouv-fr/0.1 (+https://github.com/gghez/mcp-gouv-fr)",
)
