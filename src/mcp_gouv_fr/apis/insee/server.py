"""FastMCP sub-server for INSEE API Sirene (mounted under namespace ``insee``)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastmcp import FastMCP
from fastmcp.server.context import Context

from mcp_gouv_fr.apis.insee import http as insee_http
from mcp_gouv_fr.apis.insee.config import INSEE_API_KEY, INSEE_SIRENE_API_BASE
from mcp_gouv_fr.apis.insee.models import (
    EtablissementOutput,
    EtablissementsSearchOutput,
    UniteLegaleOutput,
    UnitesLegalesSearchOutput,
)
from mcp_gouv_fr.config import HTTP_TIMEOUT_S, HTTP_USER_AGENT
from mcp_gouv_fr.http_lifespan import get_http_client


def _require_api_key() -> None:
    if not INSEE_API_KEY:
        raise RuntimeError(
            "INSEE API key is not configured. Create a subscription and key at "
            "https://portail-api.insee.fr/ then set environment variable MCP_GOUV_INSEE_API_KEY."
        )


@asynccontextmanager
async def _lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    base = INSEE_SIRENE_API_BASE.rstrip("/") + "/"
    headers: dict[str, str] = {
        "User-Agent": HTTP_USER_AGENT,
        "Accept": "application/json;charset=utf-8",
    }
    if INSEE_API_KEY:
        headers["X-INSEE-Api-Key-Integration"] = INSEE_API_KEY

    async with httpx.AsyncClient(
        base_url=base,
        timeout=HTTP_TIMEOUT_S,
        headers=headers,
    ) as client:
        server._http_client = client  # type: ignore[attr-defined]
        yield {}


def build_subserver() -> FastMCP:
    """Build the INSEE Sirene API sub-server.

    Mount on the root app with ``namespace='insee'``.
    """
    mcp = FastMCP(
        "INSEE (Sirene)",
        instructions=(
            "Look up French business registry records via INSEE API Sirene 3.11 (api.insee.fr). "
            "Subscribe and obtain an API key at https://portail-api.insee.fr/catalog/api/"
            "2ba0e549-5587-3ef1-9082-99cd865de66f and set MCP_GOUV_INSEE_API_KEY. "
            "Multicriteria search uses the official ``q`` syntax (variable:value, AND/OR, ranges, "
            "historized periode(...)); see INSEE Sirene 3.11 documentation on sirene.fr. "
            "Results may include personal or sensitive business data; comply with applicable law "
            "and INSEE terms of use. Tool docstrings and model field descriptions reflect "
            "SIREN/SIRET semantics."
        ),
        lifespan=_lifespan,
    )

    @mcp.tool
    async def get_unite_legale(ctx: Context, siren: str) -> UniteLegaleOutput:
        """Return the legal unit (unité légale) for one 9-digit SIREN.

        Use this to resolve a company identifier to its official INSEE record (status,
        denomination, activity codes, etc.). Requires a valid portal API key.

        Args:
            siren: Nine-digit SIREN (spaces optional).
        """
        _require_api_key()
        client = get_http_client(ctx)
        raw = await insee_http.get_unite_legale(client, siren)
        return UniteLegaleOutput.from_api_payload(raw)

    @mcp.tool
    async def get_etablissement(ctx: Context, siret: str) -> EtablissementOutput:
        """Return the establishment (établissement) for one 14-digit SIRET.

        Use this for a specific branch or address (SIRET includes the SIREN plus a NIC).
        Requires a valid portal API key.

        Args:
            siret: Fourteen-digit SIRET (spaces optional).
        """
        _require_api_key()
        client = get_http_client(ctx)
        raw = await insee_http.get_etablissement(client, siret)
        return EtablissementOutput.from_api_payload(raw)

    @mcp.tool
    async def search_unites_legales(
        ctx: Context,
        q: str,
        nombre: int = 20,
        debut: int = 0,
        tri: str | None = None,
        date: str | None = None,
        champs: str | None = None,
        curseur: str | None = None,
    ) -> UnitesLegalesSearchOutput:
        """Multicriteria search for legal units (unités légales) via GET ``/siren``.

        This calls the same service as the INSEE portal OpenAPI (Sirene 3.11): query string
        ``q`` uses Lucene-style criteria on Sirene field names (camelCase), e.g.
        ``denominationUniteLegale:INSEE``, ``siren:552081317``, boolean combinations with
        ``AND``/``OR``, ranges ``[min TO max]``, wildcards, and historized clauses
        ``periode(field:value)``. Optional ``date`` (AAAA-MM-JJ) selects values of historized
        variables at that date. ``nombre`` is the page size (0–200000, default 20); ``debut`` is
        the zero-based offset of the first hit (0–10000). ``tri`` is a comma-separated list of
        sort fields (default sort is by siren). ``champs`` restricts returned attributes.
        ``curseur`` enables deep pagination per INSEE documentation.

        Official catalogue and examples: https://portail-api.insee.fr/catalog/api/
        2ba0e549-5587-3ef1-9082-99cd865de66f/doc

        Args:
            q: Multicriteria query string passed to the API ``q`` parameter.
            nombre: Number of results to return (API default 20; max 200000).
            debut: Index of the first result (max 10000).
            tri: Comma-separated fields to sort by.
            date: Reference date for historized variables (AAAA-MM-JJ).
            champs: Comma-separated list of fields to return.
            curseur: Cursor for deep pagination when applicable.
        """
        _require_api_key()
        client = get_http_client(ctx)
        raw = await insee_http.search_unites_legales(
            client,
            q,
            nombre=nombre,
            debut=debut,
            tri=tri,
            date=date,
            champs=champs,
            curseur=curseur,
        )
        return UnitesLegalesSearchOutput.from_api_payload(raw)

    @mcp.tool
    async def search_etablissements(
        ctx: Context,
        q: str,
        nombre: int = 20,
        debut: int = 0,
        tri: str | None = None,
        date: str | None = None,
        champs: str | None = None,
        curseur: str | None = None,
    ) -> EtablissementsSearchOutput:
        """Multicriteria search for establishments (établissements) via GET ``/siret``.

        Same query language as legal-unit search, on establishment variables (e.g.
        ``codeCommuneEtablissement:92046``, ``siren:775672272``, ``enseigne1Etablissement:...``).
        Parameters ``nombre``, ``debut``, ``tri``, ``date``, ``champs``, and ``curseur`` match
        the official Sirene 3.11 OpenAPI for GET ``/siret``.

        Official catalogue and examples: https://portail-api.insee.fr/catalog/api/
        2ba0e549-5587-3ef1-9082-99cd865de66f/doc

        Args:
            q: Multicriteria query string passed to the API ``q`` parameter.
            nombre: Number of results to return (API default 20; max 200000).
            debut: Index of the first result (max 10000).
            tri: Comma-separated fields to sort by.
            date: Reference date for historized variables (AAAA-MM-JJ).
            champs: Comma-separated list of fields to return.
            curseur: Cursor for deep pagination when applicable.
        """
        _require_api_key()
        client = get_http_client(ctx)
        raw = await insee_http.search_etablissements(
            client,
            q,
            nombre=nombre,
            debut=debut,
            tri=tri,
            date=date,
            champs=champs,
            curseur=curseur,
        )
        return EtablissementsSearchOutput.from_api_payload(raw)

    return mcp
