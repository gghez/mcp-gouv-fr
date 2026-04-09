"""FastMCP sub-server for data.gouv.fr (mounted under namespace ``datagouv``)."""

from __future__ import annotations

import logging
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

_log = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(_server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    base = DATAGOUV_API_BASE.rstrip("/") + "/"
    _log.info("datagouv lifespan: opening HTTP client base_url=%s timeout=%s", base, HTTP_TIMEOUT_S)
    try:
        async with httpx.AsyncClient(
            base_url=base,
            timeout=HTTP_TIMEOUT_S,
            headers={"User-Agent": HTTP_USER_AGENT, "Accept": "application/json"},
        ) as client:
            _log.info("datagouv lifespan: client ready")
            yield {"http_client": client}
    except Exception:
        _log.exception("datagouv lifespan: error while managing HTTP client")
        raise
    _log.info("datagouv lifespan: HTTP client closed")


def build_subserver() -> FastMCP:
    """Build the data.gouv.fr API sub-server.

    Mount on the root app with ``namespace='datagouv'``.
    """
    _log.info("build_subserver: creating data.gouv.fr FastMCP app")
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
        _log.info(
            "tool search_datasets called query=%r page=%s page_size=%s",
            query,
            page,
            page_size,
        )
        if not query.strip():
            _log.warning("search_datasets: empty or whitespace-only query")
        if page < 1:
            _log.warning("search_datasets: page should be >= 1, got %s", page)
        if page_size < 1:
            _log.warning("search_datasets: page_size should be >= 1, got %s", page_size)
        elif page_size > 100:
            _log.warning(
                "search_datasets: page_size=%s is large; the API may cap or respond slowly",
                page_size,
            )
        client: httpx.AsyncClient = ctx.lifespan_context["http_client"]
        try:
            raw = await dg_http.search_datasets(client, query=query, page=page, page_size=page_size)
            out = DatasetSearchOutput.from_api_payload(raw)
        except Exception:
            _log.exception("tool search_datasets failed")
            raise
        _log.info(
            "tool search_datasets ok total=%s datasets_on_page=%s",
            out.total,
            len(out.datasets),
        )
        return out

    @mcp.tool
    async def get_dataset(ctx: Context, dataset_id: str) -> DatasetDetailOutput:
        """Return dataset metadata and resources for one dataset.

        Args:
            dataset_id: Dataset id or slug.
        """
        _log.info("tool get_dataset called dataset_id=%r", dataset_id)
        if not dataset_id.strip():
            _log.warning("get_dataset: empty or whitespace-only dataset_id")
        client: httpx.AsyncClient = ctx.lifespan_context["http_client"]
        try:
            raw = await dg_http.get_dataset(client, dataset_id)
            out = DatasetDetailOutput.from_api_payload(raw)
        except Exception:
            _log.exception("tool get_dataset failed dataset_id=%r", dataset_id)
            raise
        _log.info(
            "tool get_dataset ok id=%r resources=%s",
            out.id,
            len(out.resources),
        )
        return out

    _log.info("build_subserver: registered tools search_datasets, get_dataset")
    return mcp
