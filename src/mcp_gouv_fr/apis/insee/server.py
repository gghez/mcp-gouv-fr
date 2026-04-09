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
from mcp_gouv_fr.apis.insee.models import EtablissementOutput, UniteLegaleOutput
from mcp_gouv_fr.config import HTTP_TIMEOUT_S, HTTP_USER_AGENT


def _require_api_key() -> None:
    if not INSEE_API_KEY:
        raise RuntimeError(
            "INSEE API key is not configured. Create a subscription and key at "
            "https://portail-api.insee.fr/ then set environment variable MCP_GOUV_INSEE_API_KEY."
        )


@asynccontextmanager
async def _lifespan(_server: FastMCP) -> AsyncIterator[dict[str, Any]]:
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
        yield {"http_client": client}


def build_subserver() -> FastMCP:
    """Build the INSEE Sirene API sub-server.

    Mount on the root app with ``namespace='insee'``.
    """
    mcp = FastMCP(
        "INSEE (Sirene)",
        instructions=(
            "Look up French business registry records via INSEE API Sirene 3.11 (api.insee.fr). "
            "Subscribe and obtain an API key at https://portail-api.insee.fr/ and set "
            "MCP_GOUV_INSEE_API_KEY. Results may include personal or sensitive business data; "
            "comply with applicable law and INSEE terms of use. "
            "Tool docstrings and model field descriptions reflect SIREN/SIRET semantics."
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
        client: httpx.AsyncClient = ctx.lifespan_context["http_client"]
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
        client: httpx.AsyncClient = ctx.lifespan_context["http_client"]
        raw = await insee_http.get_etablissement(client, siret)
        return EtablissementOutput.from_api_payload(raw)

    return mcp
