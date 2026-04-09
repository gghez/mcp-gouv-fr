"""Unit tests for data.gouv.fr HTTP helpers."""

from __future__ import annotations

import httpx
import pytest

from mcp_gouv_fr.apis.datagouv import http as dg_http


def _mock_transport(payload: dict) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "/datasets" in request.url.path
        return httpx.Response(200, json=payload)

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_search_datasets_parses_json() -> None:
    expected = {"data": [{"id": "x", "title": "Test"}]}
    transport = _mock_transport(expected)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://www.data.gouv.fr/api/1/",
    ) as client:
        result = await dg_http.search_datasets(client, query="impots", page=1, page_size=10)
    assert result == expected


@pytest.mark.asyncio
async def test_get_dataset_by_id() -> None:
    expected = {"id": "abc", "title": "Sample dataset"}
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=expected)
        if request.url.path.rstrip("/").endswith("/datasets/abc")
        else httpx.Response(404)
    )
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://www.data.gouv.fr/api/1/",
    ) as client:
        result = await dg_http.get_dataset(client, "abc")
    assert result == expected
