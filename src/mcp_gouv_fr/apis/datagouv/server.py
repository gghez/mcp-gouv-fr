"""FastMCP sub-server for data.gouv.fr (mounted under namespace ``datagouv``)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastmcp import FastMCP
from fastmcp.server.context import Context

from mcp_gouv_fr.apis.datagouv import http as dg_http
from mcp_gouv_fr.apis.datagouv.config import DATAGOUV_API_BASE
from mcp_gouv_fr.apis.datagouv.models import DatasetDetailOutput, DatasetSearchOutput
from mcp_gouv_fr.config import HTTP_TIMEOUT_S, HTTP_USER_AGENT


@asynccontextmanager
async def _lifespan(_server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    async with httpx.AsyncClient(
        base_url=DATAGOUV_API_BASE.rstrip("/") + "/",
        timeout=HTTP_TIMEOUT_S,
        headers={"User-Agent": HTTP_USER_AGENT, "Accept": "application/json"},
    ) as client:
        yield {"http_client": client}


def build_subserver() -> FastMCP:
    """Build the data.gouv.fr API sub-server.

    Mount on the root app with ``namespace='datagouv'``.
    """
    mcp = FastMCP(
        "data.gouv.fr",
        instructions=(
            "Search and inspect datasets on the French national open data portal (data.gouv.fr). "
            "Use structured results for pagination and follow-up detail lookups. "
            "Tool docstrings, Pydantic model docstrings, and per-field descriptions define the "
            "meaning of each value—use them for discovery and correct interpretation."
        ),
        lifespan=_lifespan,
    )

    @mcp.tool
    async def search_datasets(
        ctx: Context,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> DatasetSearchOutput:
        """Search datasets (title, description, organization).

        Args:
            query: Free-text search query.
            page: Page number (1-based).
            page_size: Page size (keep reasonably small, e.g. ≤ 100).
        """
        client: httpx.AsyncClient = ctx.lifespan_context["http_client"]
        raw = await dg_http.search_datasets(client, query=query, page=page, page_size=page_size)
        return DatasetSearchOutput.from_api_payload(raw)

    @mcp.tool
    async def get_dataset(ctx: Context, dataset_id: str) -> DatasetDetailOutput:
        """Return dataset metadata and resources for one dataset.

        Args:
            dataset_id: Dataset id or slug.
        """
        client: httpx.AsyncClient = ctx.lifespan_context["http_client"]
        raw = await dg_http.get_dataset(client, dataset_id)
        return DatasetDetailOutput.from_api_payload(raw)

    return mcp
