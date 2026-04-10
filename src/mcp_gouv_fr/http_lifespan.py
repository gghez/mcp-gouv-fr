"""Resolve the shared HTTP client from FastMCP lifespan (API sub-servers)."""

from __future__ import annotations

import httpx
from fastmcp.server.context import Context

_MISSING_HTTP_CLIENT = (
    "MCP lifespan did not provide a usable 'http_client'. "
    "Pass lifespan=... to FastMCP and yield {'http_client': httpx.AsyncClient(...)} "
    "(see apis/datagouv/server.py)."
)


def get_lifespan_http_client(ctx: Context) -> httpx.AsyncClient:
    """Return the AsyncClient created by this sub-server's lifespan.

    Raises:
        RuntimeError: If lifespan was not wired or did not yield ``http_client``.
    """
    client = ctx.lifespan_context.get("http_client")
    if not isinstance(client, httpx.AsyncClient):
        raise RuntimeError(_MISSING_HTTP_CLIENT)
    return client
