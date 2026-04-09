"""Smoke tests for MCP server construction."""

from __future__ import annotations

import pytest

from mcp_gouv_fr.server import build_server


@pytest.mark.asyncio
async def test_build_server_has_tools() -> None:
    mcp = build_server()
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert "datagouv_search_datasets" in names
    assert "datagouv_get_dataset" in names
    assert "insee_get_unite_legale" in names
    assert "insee_get_etablissement" in names


@pytest.mark.asyncio
async def test_tools_expose_pydantic_output_schema() -> None:
    mcp = build_server()
    tools = {t.name: t for t in await mcp.list_tools()}
    search = tools["datagouv_search_datasets"]
    get_ds = tools["datagouv_get_dataset"]
    insee_ul = tools["insee_get_unite_legale"]
    assert search.output_schema is not None
    assert get_ds.output_schema is not None
    assert insee_ul.output_schema is not None
    props = search.output_schema.get("properties", {})
    assert "datasets" in props


@pytest.mark.asyncio
async def test_build_server_custom_mounts_empty_has_no_tools() -> None:
    mcp = build_server(api_mounts=())
    tools = await mcp.list_tools()
    assert tools == []
