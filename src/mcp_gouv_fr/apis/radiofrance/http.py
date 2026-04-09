"""Async HTTP calls to the Radio France Open API (GraphQL over HTTP POST)."""

from __future__ import annotations

from typing import Any

import httpx


async def execute_graphql(
    client: httpx.AsyncClient,
    url: str,
    query: str,
    variables: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a GraphQL operation and return the JSON body (``data`` / ``errors``)."""
    payload: dict[str, Any] = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    response = await client.post(url, json=payload)
    response.raise_for_status()
    body = response.json()
    if not isinstance(body, dict):
        msg = "Radio France GraphQL response must be a JSON object"
        raise ValueError(msg)
    return body
