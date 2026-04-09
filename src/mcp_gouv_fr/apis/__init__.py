"""Government API packages (one subdirectory per portal or API family).

Each subdirectory under ``mcp_gouv_fr.apis`` is a self-contained package
(models, HTTP helpers, optional config) that exposes a ``build_subserver()``
function returning a ``FastMCP`` instance.

Register APIs in :func:`default_api_mounts` so the root server mounts them
with a namespace prefix (e.g. ``datagouv_search_datasets``).

New API packages must follow AGENTS.md: documented tools, models, and every model field
(``Field(description=...)``) for agent discovery.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from fastmcp import FastMCP

type ApiMount = tuple[str, Callable[[], FastMCP]]


def default_api_mounts() -> Sequence[ApiMount]:
    """Ordered list of (namespace, subserver_factory) for the composite MCP server."""
    from mcp_gouv_fr.apis.datagouv.server import build_subserver as build_datagouv
    from mcp_gouv_fr.apis.geo.server import build_subserver as build_geo
    from mcp_gouv_fr.apis.radiofrance.server import build_subserver as build_radiofrance

    return (
        ("datagouv", build_datagouv),
        ("radiofrance", build_radiofrance),
        ("geo", build_geo),
    )
