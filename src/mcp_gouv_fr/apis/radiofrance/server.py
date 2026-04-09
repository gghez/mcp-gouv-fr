"""FastMCP sub-server for Radio France Open API (mounted under namespace ``radiofrance``)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastmcp import FastMCP
from fastmcp.server.context import Context

from mcp_gouv_fr.apis.radiofrance import http as rf_http
from mcp_gouv_fr.apis.radiofrance.config import RADIOFRANCE_API_TOKEN, RADIOFRANCE_GRAPHQL_URL
from mcp_gouv_fr.apis.radiofrance.models import GraphQLExecuteOutput
from mcp_gouv_fr.config import HTTP_TIMEOUT_S, HTTP_USER_AGENT


@asynccontextmanager
async def _lifespan(_server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    headers: dict[str, str] = {
        "User-Agent": HTTP_USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if RADIOFRANCE_API_TOKEN:
        headers["x-token"] = RADIOFRANCE_API_TOKEN
    async with httpx.AsyncClient(
        timeout=HTTP_TIMEOUT_S,
        headers=headers,
    ) as client:
        yield {"http_client": client, "graphql_url": RADIOFRANCE_GRAPHQL_URL.rstrip("/")}


def build_subserver() -> FastMCP:
    """Build the Radio France Open API sub-server.

    Mount on the root app with ``namespace='radiofrance'``.
    """
    mcp = FastMCP(
        "Radio France Open API",
        instructions=(
            "Query program grids, stations, shows, and podcasts via the Radio France GraphQL API. "
            "Requires ``MCP_GOUV_RADIOFRANCE_API_TOKEN`` "
            "(request a key at https://developers.radiofrance.fr/). "
            "Explore the schema with the official GraphiQL URL documented there "
            "(pass ``x-token``). "
            "Tool docstrings, model docstrings, and field descriptions define result semantics."
        ),
        lifespan=_lifespan,
    )

    @mcp.tool
    async def graphql(
        ctx: Context,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> GraphQLExecuteOutput:
        """Execute a GraphQL query or mutation against the Radio France Open API.

        The upstream API is documented at https://developers.radiofrance.fr/ (programs, channels,
        podcasts). Use introspection or the hosted explorer (with your API token) to discover
        fields and types.

        Args:
            query: GraphQL document (query or mutation).
            variables: Optional variables object; omit or pass empty dict when the query has none.
        """
        if not RADIOFRANCE_API_TOKEN:
            msg = (
                "Missing MCP_GOUV_RADIOFRANCE_API_TOKEN. Request an API key at "
                "https://developers.radiofrance.fr/ and set the variable in your environment."
            )
            raise RuntimeError(msg)
        client: httpx.AsyncClient = ctx.lifespan_context["http_client"]
        graphql_url: str = ctx.lifespan_context["graphql_url"]
        raw = await rf_http.execute_graphql(
            client,
            graphql_url,
            query=query,
            variables=variables,
        )
        return GraphQLExecuteOutput.from_api_payload(raw)

    return mcp
