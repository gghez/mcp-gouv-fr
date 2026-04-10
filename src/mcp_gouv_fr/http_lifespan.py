"""Resolve the shared HTTP client stored on the FastMCP sub-server instance."""

from __future__ import annotations

import httpx
from fastmcp.server.context import Context


def get_http_client(ctx: Context) -> httpx.AsyncClient:
    """Return the ``httpx.AsyncClient`` stored on the sub-server by its lifespan.

    Each sub-server lifespan sets ``server._http_client`` before yielding.
    Tools retrieve it here via ``ctx.fastmcp`` (the sub-server instance).

    Raises:
        RuntimeError: If the lifespan did not store a client.
    """
    client = getattr(ctx.fastmcp, "_http_client", None)
    if not isinstance(client, httpx.AsyncClient):
        raise RuntimeError(
            "No HTTP client on this sub-server. "
            "The lifespan must set server._http_client = httpx.AsyncClient(...)."
        )
    return client
