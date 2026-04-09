"""Async HTTP calls to the data.gouv.fr API (v1)."""

from __future__ import annotations

from typing import Any

import httpx


async def search_datasets(
    client: httpx.AsyncClient,
    query: str,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """Fetch dataset search results as raw JSON."""
    response = await client.get(
        "/datasets/",
        params={"q": query, "page": page, "page_size": page_size},
    )
    response.raise_for_status()
    return response.json()


async def get_dataset(client: httpx.AsyncClient, dataset_id: str) -> dict[str, Any]:
    """Fetch one dataset by id or slug as raw JSON."""
    response = await client.get(f"/datasets/{dataset_id}/")
    response.raise_for_status()
    return response.json()
