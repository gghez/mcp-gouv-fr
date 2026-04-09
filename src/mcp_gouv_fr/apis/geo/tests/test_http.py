"""Unit tests for geo.api.gouv.fr HTTP helpers."""

from __future__ import annotations

import httpx
import pytest

from mcp_gouv_fr.apis.geo import http as geo_http

_GEO_BASE = "https://geo.api.gouv.fr/"


@pytest.mark.asyncio
async def test_search_communes_builds_query() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(dict(request.url.params))
        assert request.url.path.rstrip("/").endswith("/communes")
        return httpx.Response(200, json=[{"nom": "X", "code": "12345"}])

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url=_GEO_BASE) as client:
        result = await geo_http.search_communes(
            client,
            nom="Test",
            code_postal="75001",
            code_departement="75",
            limit=5,
        )
    assert result == [{"nom": "X", "code": "12345"}]
    assert captured.get("nom") == "Test"
    assert captured.get("codePostal") == "75001"
    assert captured.get("codeDepartement") == "75"
    assert captured.get("limit") == "5"
    assert captured.get("boost") == "population"


@pytest.mark.asyncio
async def test_get_commune_by_code() -> None:
    expected = {"nom": "Paris", "code": "75056"}
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=expected)
        if request.url.path.rstrip("/").endswith("/communes/75056")
        else httpx.Response(404)
    )
    async with httpx.AsyncClient(transport=transport, base_url=_GEO_BASE) as client:
        result = await geo_http.get_commune(client, "75056")
    assert result == expected


@pytest.mark.asyncio
async def test_search_departements() -> None:
    expected = [{"nom": "Paris", "code": "75"}]
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json=expected))
    async with httpx.AsyncClient(transport=transport, base_url=_GEO_BASE) as client:
        result = await geo_http.search_departements(client, nom="Paris")
    assert result == expected


@pytest.mark.asyncio
async def test_get_departement() -> None:
    expected = {"nom": "Paris", "code": "75", "region": {"code": "11", "nom": "IdF"}}
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=expected)
        if request.url.path.rstrip("/").endswith("/departements/75")
        else httpx.Response(404)
    )
    async with httpx.AsyncClient(transport=transport, base_url=_GEO_BASE) as client:
        result = await geo_http.get_departement(client, "75")
    assert result == expected


@pytest.mark.asyncio
async def test_search_regions() -> None:
    expected = [{"nom": "Île-de-France", "code": "11"}]
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json=expected))
    async with httpx.AsyncClient(transport=transport, base_url=_GEO_BASE) as client:
        result = await geo_http.search_regions(client)
    assert result == expected


@pytest.mark.asyncio
async def test_get_region() -> None:
    expected = {"nom": "Île-de-France", "code": "11"}
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=expected)
        if request.url.path.rstrip("/").endswith("/regions/11")
        else httpx.Response(404)
    )
    async with httpx.AsyncClient(transport=transport, base_url=_GEO_BASE) as client:
        result = await geo_http.get_region(client, "11")
    assert result == expected
