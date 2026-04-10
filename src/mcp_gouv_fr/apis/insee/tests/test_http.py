"""Unit tests for INSEE Sirene HTTP helpers."""

from __future__ import annotations

import httpx
import pytest

from mcp_gouv_fr.apis.insee import http as insee_http


@pytest.mark.asyncio
async def test_get_unite_legale_parses_json() -> None:
    expected = {"uniteLegale": {"siren": "123456789", "denominationUniteLegale": "ACME"}}
    transport = httpx.MockTransport(
        lambda request: (
            httpx.Response(200, json=expected)
            if request.url.path.rstrip("/").endswith("/siren/123456789")
            else httpx.Response(404)
        )
    )
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.insee.fr/api-sirene/3.11/",
    ) as client:
        result = await insee_http.get_unite_legale(client, "123 456 789")
    assert result == expected


@pytest.mark.asyncio
async def test_get_etablissement_parses_json() -> None:
    expected = {"siret": "12345678901234", "etablissement": {"siret": "12345678901234"}}
    transport = httpx.MockTransport(
        lambda request: (
            httpx.Response(200, json=expected)
            if request.url.path.rstrip("/").endswith("/siret/12345678901234")
            else httpx.Response(404)
        )
    )
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.insee.fr/api-sirene/3.11/",
    ) as client:
        result = await insee_http.get_etablissement(client, "123 456 789 01234")
    assert result == expected


def test_normalize_siren_invalid() -> None:
    with pytest.raises(ValueError, match="9"):
        insee_http.normalize_siren("123")


def test_normalize_siret_invalid() -> None:
    with pytest.raises(ValueError, match="14"):
        insee_http.normalize_siret("123")


def test_normalize_search_query_empty() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        insee_http.normalize_search_query("   ")


def test_search_params_nombre_out_of_range() -> None:
    with pytest.raises(ValueError, match="nombre"):
        insee_http._search_params(
            q="siren:123456789",
            nombre=200_001,
            debut=0,
            tri=None,
            date=None,
            champs=None,
            curseur=None,
        )


def test_search_params_debut_out_of_range() -> None:
    with pytest.raises(ValueError, match="debut"):
        insee_http._search_params(
            q="siren:123456789",
            nombre=20,
            debut=10_001,
            tri=None,
            date=None,
            champs=None,
            curseur=None,
        )


@pytest.mark.asyncio
async def test_search_unites_legales_builds_query() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path.rstrip("/")
        q = request.url.params.get("q")
        assert q == "denominationUniteLegale:INSEE"
        assert request.url.params.get("nombre") == "5"
        assert request.url.params.get("debut") == "10"
        assert request.url.params.get("tri") == "siren"
        assert request.url.params.get("date") == "2024-01-15"
        assert request.url.params.get("champs") == "siren,denominationUniteLegale"
        assert request.url.params.get("curseur") == "abc"
        return httpx.Response(
            200,
            json={
                "header": {"total": 1, "debut": 10, "nombre": 5},
                "unitesLegales": [{"siren": "552081317"}],
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.insee.fr/api-sirene/3.11/",
    ) as client:
        result = await insee_http.search_unites_legales(
            client,
            "denominationUniteLegale:INSEE",
            nombre=5,
            debut=10,
            tri="siren",
            date="2024-01-15",
            champs="siren,denominationUniteLegale",
            curseur="abc",
        )
    assert captured["path"].endswith("/siren")
    assert result["unitesLegales"][0]["siren"] == "552081317"


@pytest.mark.asyncio
async def test_search_etablissements_builds_query() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.rstrip("/").endswith("/siret")
        assert request.url.params.get("q") == "codeCommuneEtablissement:92046"
        return httpx.Response(
            200,
            json={
                "header": {"total": 2, "debut": 0, "nombre": 20},
                "etablissements": [{"siret": "123"}, {"siret": "456"}],
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.insee.fr/api-sirene/3.11/",
    ) as client:
        result = await insee_http.search_etablissements(client, "codeCommuneEtablissement:92046")
    assert len(result["etablissements"]) == 2
