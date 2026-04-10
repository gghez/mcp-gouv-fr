"""Resolve the shared HTTP client from FastMCP lifespan (API sub-servers)."""

from __future__ import annotations

from typing import Any

import httpx
from fastmcp.server.context import Context

_MISSING_HTTP_CLIENT = (
    "MCP lifespan did not provide a usable 'http_client'. "
    "Pass lifespan=... to FastMCP and yield {'http_client': httpx.AsyncClient(...)} "
    "(see apis/datagouv/server.py)."
)


def effective_lifespan_context(ctx: Context) -> dict[str, Any]:
    """Lifespan key/value dict visible to tools on this FastMCP app.

    For a **composite** server (root mounts API sub-servers), MCP request scope still
    carries the **root** ``lifespan_context`` (often empty). Each mounted sub-server
    stores its own ``yield {...}`` result on ``FastMCP._lifespan_result`` after
    startup. Tools run with ``Context(fastmcp=sub_server)`` but
    ``Context.lifespan_context`` reads the request first, so we merge request data
    with ``_lifespan_result`` so ``http_client`` and API-specific keys resolve.
    """
    from_request: dict[str, Any] = {}
    rc = ctx.request_context
    if rc is not None:
        lc = rc.lifespan_context
        if isinstance(lc, dict):
            from_request = dict(lc)
    stored = getattr(ctx.fastmcp, "_lifespan_result", None)
    if isinstance(stored, dict):
        return {**from_request, **stored}
    return from_request


def get_lifespan_http_client(ctx: Context) -> httpx.AsyncClient:
    """Return the AsyncClient created by this sub-server's lifespan.

    Raises:
        RuntimeError: If lifespan was not wired or did not yield ``http_client``.
    """
    data = effective_lifespan_context(ctx)
    client = data.get("http_client")
    if not isinstance(client, httpx.AsyncClient):
        raise RuntimeError(_MISSING_HTTP_CLIENT)
    return client
