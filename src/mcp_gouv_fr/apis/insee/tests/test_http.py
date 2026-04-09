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
