"""Root FastMCP server: mounts one sub-server per government API package."""

from __future__ import annotations

from collections.abc import Sequence

from fastmcp import FastMCP

from mcp_gouv_fr.apis import ApiMount, default_api_mounts


def build_server(*, api_mounts: Sequence[ApiMount] | None = None) -> FastMCP:
    """Create the composite MCP app and mount all registered API packages.

    Each API is a separate Python package under ``mcp_gouv_fr.apis`` with its own
    ``build_subserver()`` and optional lifespan. FastMCP prefixes tool names with the
    namespace (e.g. ``datagouv_search_datasets``).

    Args:
        api_mounts: Override for tests; defaults to :func:`default_api_mounts`.
    """
    if api_mounts is None:
        mounts = list(default_api_mounts())
    else:
        mounts = list(api_mounts)

    mcp = FastMCP(
        "MCP Gouv FR",
        instructions=(
            "French public-sector open data and APIs. Tools are grouped by namespace: "
            "each prefix (e.g. ``datagouv_``, ``geo_``, ``insee_``, ``radiofrance_``) identifies "
            "one portal or API family. "
            "Use structured tool outputs and pagination fields when provided. "
            "Every tool, output model, and model field in this server is documented (descriptions "
            "and docstrings) so agents can discover semantics, units, and relationships without "
            "guessing—rely on those descriptions when interpreting results. "
            "Automated tests live in nested ``tests`` packages next to the modules they cover: "
            "e.g. ``mcp_gouv_fr/tests/`` for package-level code such as ``server.py``, and "
            "``mcp_gouv_fr/apis/datagouv/tests/``, ``mcp_gouv_fr/apis/geo/tests/``, "
            "``mcp_gouv_fr/apis/insee/tests/``, ``mcp_gouv_fr/apis/radiofrance/tests/`` alongside "
            "``http.py``, ``models.py``, and other siblings in that API package."
        ),
    )

    for namespace, factory in mounts:
        mcp.mount(factory(), namespace=namespace)

    return mcp
