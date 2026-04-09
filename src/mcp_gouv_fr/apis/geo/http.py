"""Async HTTP calls to the French geographic referential API (geo.api.gouv.fr)."""

from __future__ import annotations

from typing import Any

import httpx


async def search_communes(
    client: httpx.AsyncClient,
    *,
    nom: str | None = None,
    code_postal: str | None = None,
    code_departement: str | None = None,
    boost_population: bool = True,
    limit: int = 10,
    fields: str = "nom,code,codesPostaux,departement,region",
) -> list[dict[str, Any]]:
    """Fetch communes matching optional filters; response is a JSON array."""
    params: dict[str, Any] = {"limit": limit, "fields": fields}
    if nom is not None and nom != "":
        params["nom"] = nom
    if code_postal is not None and code_postal != "":
        params["codePostal"] = code_postal
    if code_departement is not None and code_departement != "":
        params["codeDepartement"] = code_departement
    if boost_population:
        params["boost"] = "population"
    response = await client.get("/communes", params=params)
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, list) else []


async def get_commune(
    client: httpx.AsyncClient,
    code: str,
    *,
    fields: str = "nom,code,codesPostaux,departement,region,population,surface",
) -> dict[str, Any]:
    """Fetch one commune by INSEE municipality code (``code`` path segment)."""
    response = await client.get(f"/communes/{code}", params={"fields": fields})
    response.raise_for_status()
    return response.json()


async def search_departements(
    client: httpx.AsyncClient,
    *,
    nom: str | None = None,
    limit: int = 120,
    fields: str = "nom,code,region",
) -> list[dict[str, Any]]:
    """List or search departments (``nom`` triggers fuzzy search when set)."""
    params: dict[str, Any] = {"limit": limit, "fields": fields}
    if nom is not None and nom != "":
        params["nom"] = nom
    response = await client.get("/departements", params=params)
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, list) else []


async def get_departement(
    client: httpx.AsyncClient,
    code: str,
    *,
    fields: str = "nom,code,region",
) -> dict[str, Any]:
    """Fetch one department by official code (e.g. ``75``, ``2A``)."""
    response = await client.get(f"/departements/{code}", params={"fields": fields})
    response.raise_for_status()
    return response.json()


async def search_regions(
    client: httpx.AsyncClient,
    *,
    nom: str | None = None,
    limit: int = 30,
    fields: str = "nom,code",
) -> list[dict[str, Any]]:
    """List or search regions (``nom`` triggers fuzzy search when set)."""
    params: dict[str, Any] = {"limit": limit, "fields": fields}
    if nom is not None and nom != "":
        params["nom"] = nom
    response = await client.get("/regions", params=params)
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, list) else []


async def get_region(
    client: httpx.AsyncClient,
    code: str,
    *,
    fields: str = "nom,code",
) -> dict[str, Any]:
    """Fetch one region by official code (e.g. ``11`` for Île-de-France)."""
    response = await client.get(f"/regions/{code}", params={"fields": fields})
    response.raise_for_status()
    return response.json()
