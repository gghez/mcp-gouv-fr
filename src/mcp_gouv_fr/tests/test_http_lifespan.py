"""Tests for get_http_client (server-instance-based resolution)."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from mcp_gouv_fr.http_lifespan import get_http_client


def _fake_ctx(*, http_client: object | None = None) -> MagicMock:
    """Minimal stand-in for fastmcp Context."""
    ctx = MagicMock()
    if http_client is not None:
        ctx.fastmcp._http_client = http_client
    else:
        del ctx.fastmcp._http_client
    return ctx


@pytest.mark.asyncio
async def test_get_http_client_returns_stored_client() -> None:
    async with httpx.AsyncClient() as real_client:
        ctx = _fake_ctx(http_client=real_client)
        assert get_http_client(ctx) is real_client


def test_get_http_client_raises_when_missing() -> None:
    ctx = _fake_ctx()
    with pytest.raises(RuntimeError, match="No HTTP client"):
        get_http_client(ctx)


def test_get_http_client_raises_when_wrong_type() -> None:
    ctx = _fake_ctx(http_client="not a client")
    with pytest.raises(RuntimeError, match="No HTTP client"):
        get_http_client(ctx)
