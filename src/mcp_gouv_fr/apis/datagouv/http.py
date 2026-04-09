"""Async HTTP calls to the data.gouv.fr API (v1)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

_log = logging.getLogger(__name__)


def _response_error_detail(response: httpx.Response, *, max_len: int = 500) -> str:
    text = response.text or ""
    if len(text) > max_len:
        return f"{text[:max_len]}... (truncated)"
    return text


async def search_datasets(
    client: httpx.AsyncClient,
    query: str,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """Fetch dataset search results as raw JSON."""
    url = "/datasets/"
    params = {"q": query, "page": page, "page_size": page_size}
    _log.info("HTTP GET %s params=%s", url, params)
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        _log.error(
            "search_datasets HTTP error: %s %s body=%s",
            e.response.status_code,
            e.response.reason_phrase,
            _response_error_detail(e.response),
        )
        raise
    except httpx.RequestError as e:
        _log.error("search_datasets request failed: %s", e)
        raise
    _log.info("search_datasets: status=%s", response.status_code)
    try:
        return response.json()
    except ValueError as e:
        _log.error("search_datasets: invalid JSON in response: %s", e)
        raise


async def get_dataset(client: httpx.AsyncClient, dataset_id: str) -> dict[str, Any]:
    """Fetch one dataset by id or slug as raw JSON."""
    path = f"/datasets/{dataset_id}/"
    _log.info("HTTP GET %s", path)
    try:
        response = await client.get(path)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        _log.error(
            "get_dataset HTTP error: %s %s dataset_id=%r body=%s",
            e.response.status_code,
            e.response.reason_phrase,
            dataset_id,
            _response_error_detail(e.response),
        )
        raise
    except httpx.RequestError as e:
        _log.error("get_dataset request failed: dataset_id=%r err=%s", dataset_id, e)
        raise
    _log.info("get_dataset: status=%s dataset_id=%r", response.status_code, dataset_id)
    try:
        return response.json()
    except ValueError as e:
        _log.error("get_dataset: invalid JSON for dataset_id=%r: %s", dataset_id, e)
        raise
