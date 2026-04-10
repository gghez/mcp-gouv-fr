"""FastMCP sub-server for geo.api.gouv.fr (mounted under namespace ``geo``)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastmcp import FastMCP
from fastmcp.server.context import Context

from mcp_gouv_fr.apis.geo import http as geo_http
from mcp_gouv_fr.apis.geo.config import GEO_API_BASE
from mcp_gouv_fr.apis.geo.models import (
    CommuneSearchOutput,
    CommuneSummary,
    DepartementSearchOutput,
    DepartementSummary,
    RegionSearchOutput,
    RegionSummary,
)
from mcp_gouv_fr.config import HTTP_TIMEOUT_S, HTTP_USER_AGENT
from mcp_gouv_fr.http_lifespan import get_lifespan_http_client


@asynccontextmanager
async def _lifespan(_server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    try:
        async with httpx.AsyncClient(
            base_url=GEO_API_BASE.rstrip("/") + "/",
            timeout=HTTP_TIMEOUT_S,
            headers={"User-Agent": HTTP_USER_AGENT, "Accept": "application/json"},
        ) as client:
            yield {"http_client": client}
    except Exception:
        raise


def build_subserver() -> FastMCP:
    """Build the geo.api.gouv.fr API sub-server.

    Mount on the root app with ``namespace='geo'``.
    """
    mcp = FastMCP(
        "geo.api.gouv.fr",
        instructions=(
            "French administrative geography (communes, departments, regions) via the national "
            "Geo API. Use INSEE codes for stable identifiers; use name or postal code search to "
            "resolve ambiguous labels. Tool docstrings, model docstrings, and field descriptions "
            "define semantics—read them before interpreting scores or administrative hierarchy."
        ),
        lifespan=_lifespan,
    )

    @mcp.tool
    async def search_communes(
        ctx: Context,
        nom: str | None = None,
        code_postal: str | None = None,
        code_departement: str | None = None,
        boost_population: bool = True,
        limit: int = 10,
    ) -> CommuneSearchOutput:
        """Search communes by name, postal code, and/or parent department.

        At least one of ``nom``, ``code_postal``, or ``code_departement`` must be non-empty so the
        query stays bounded (the upstream API can return very large slices without filters).

        Args:
            nom: Substring or fuzzy name (e.g. ``Paris``); optional if other filters are set.
            code_postal: Five-digit postal code; optional if other filters are set.
            code_departement: Department code (e.g. ``75``); optional if other filters are set.
            boost_population: When true, rank name search by population (upstream ``boost`` param).
            limit: Maximum number of results (keep small, e.g. ≤ 50).
        """
        if (
            not (nom or "").strip()
            and not (code_postal or "").strip()
            and not (code_departement or "").strip()
        ):
            raise ValueError(
                "Provide at least one of nom, code_postal, or code_departement for commune search."
            )
        client = get_lifespan_http_client(ctx)
        raw = await geo_http.search_communes(
            client,
            nom=nom,
            code_postal=code_postal,
            code_departement=code_departement,
            boost_population=boost_population,
            limit=limit,
        )
        return CommuneSearchOutput.from_api_list(raw)

    @mcp.tool
    async def get_commune(ctx: Context, code: str) -> CommuneSummary:
        """Return one commune by INSEE municipality code.

        Args:
            code: INSEE ``code commune`` (5 characters for mainland; includes Corsica ``2A``/``2B``
                departments’ communes with standard 5-digit codes).
        """
        client = get_lifespan_http_client(ctx)
        raw = await geo_http.get_commune(client, code)
        return CommuneSummary.model_validate(raw)

    @mcp.tool
    async def search_departements(
        ctx: Context,
        nom: str | None = None,
        limit: int = 120,
    ) -> DepartementSearchOutput:
        """List all departments or fuzzy-search them by name.

        Args:
            nom: When set, filters departments by name; when omitted, returns the full list
                (subject to ``limit``).
            limit: Cap on returned rows (default covers all mainland + overseas departments).
        """
        client = get_lifespan_http_client(ctx)
        raw = await geo_http.search_departements(client, nom=nom, limit=limit)
        return DepartementSearchOutput.from_api_list(raw)

    @mcp.tool
    async def get_departement(ctx: Context, code: str) -> DepartementSummary:
        """Return one department by code, including its region when available.

        Args:
            code: Official department code (e.g. ``13``, ``75``, ``2A``).
        """
        client = get_lifespan_http_client(ctx)
        raw = await geo_http.get_departement(client, code)
        return DepartementSummary.model_validate(raw)

    @mcp.tool
    async def search_regions(
        ctx: Context,
        nom: str | None = None,
        limit: int = 30,
    ) -> RegionSearchOutput:
        """List all regions or fuzzy-search them by name.

        Args:
            nom: When set, filters regions by name; when omitted, returns every region.
            limit: Cap on returned rows (France has fewer than 20 regions).
        """
        client = get_lifespan_http_client(ctx)
        raw = await geo_http.search_regions(client, nom=nom, limit=limit)
        return RegionSearchOutput.from_api_list(raw)

    @mcp.tool
    async def get_region(ctx: Context, code: str) -> RegionSummary:
        """Return one region by code.

        Args:
            code: Official region code (e.g. ``11`` for Île-de-France).
        """
        client = get_lifespan_http_client(ctx)
        raw = await geo_http.get_region(client, code)
        return RegionSummary.model_validate(raw)

    return mcp
