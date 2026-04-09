"""Unit tests for Radio France Open API HTTP helpers."""

from __future__ import annotations

import json

import httpx
import pytest

from mcp_gouv_fr.apis.radiofrance import http as rf_http


@pytest.mark.asyncio
async def test_execute_graphql_posts_json_body() -> None:
    expected = {"data": {"stations": []}}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == "https://openapi.radiofrance.fr/v1/graphql"
        parsed = json.loads(request.content.decode())
        assert parsed["query"] == "{ __typename }"
        assert "variables" not in parsed
        return httpx.Response(200, json=expected)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await rf_http.execute_graphql(
            client,
            "https://openapi.radiofrance.fr/v1/graphql",
            query="{ __typename }",
        )
    assert result == expected


@pytest.mark.asyncio
async def test_execute_graphql_includes_variables() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        parsed = json.loads(request.content.decode())
        assert parsed["variables"] == {"id": "x"}
        return httpx.Response(200, json={"data": {}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        await rf_http.execute_graphql(
            client,
            "https://openapi.radiofrance.fr/v1/graphql",
            query="query($id: ID!) { node(id: $id) { id } }",
            variables={"id": "x"},
        )
