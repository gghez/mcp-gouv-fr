"""Tests for composite-server lifespan resolution."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from mcp_gouv_fr.http_lifespan import effective_lifespan_context, get_lifespan_http_client


class _FakeRC:
    def __init__(self, lifespan_context: dict) -> None:
        self.lifespan_context = lifespan_context


class _FakeCtx:
    """Minimal stand-in for fastmcp Context (no full MCP session)."""

    def __init__(
        self,
        *,
        request_lifespan: dict | None,
        lifespan_result: dict | None,
    ) -> None:
        self._request_lifespan = request_lifespan
        self.fastmcp = MagicMock()
        self.fastmcp._lifespan_result = lifespan_result

    @property
    def request_context(self):
        if self._request_lifespan is None:
            return None
        return _FakeRC(self._request_lifespan)


def test_effective_lifespan_merges_request_and_stored() -> None:
    client = object()
    ctx = _FakeCtx(
        request_lifespan={"other": 1},
        lifespan_result={"http_client": client},
    )
    merged = effective_lifespan_context(ctx)  # type: ignore[arg-type]
    assert merged == {"other": 1, "http_client": client}


def test_effective_lifespan_stored_wins_on_key_overlap() -> None:
    a = object()
    b = object()
    ctx = _FakeCtx(
        request_lifespan={"http_client": a},
        lifespan_result={"http_client": b},
    )
    merged = effective_lifespan_context(ctx)  # type: ignore[arg-type]
    assert merged["http_client"] is b


@pytest.mark.asyncio
async def test_get_lifespan_http_client_uses_stored_when_request_empty() -> None:
    async with httpx.AsyncClient() as real_client:
        ctx = _FakeCtx(
            request_lifespan={},
            lifespan_result={"http_client": real_client},
        )
        got = get_lifespan_http_client(ctx)  # type: ignore[arg-type]
        assert got is real_client


def test_get_lifespan_http_client_raises_when_missing() -> None:
    ctx = _FakeCtx(request_lifespan={}, lifespan_result={})
    with pytest.raises(RuntimeError, match="http_client"):
        get_lifespan_http_client(ctx)  # type: ignore[arg-type]
