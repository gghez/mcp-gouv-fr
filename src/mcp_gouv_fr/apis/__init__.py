"""Government API packages (one subdirectory per portal or API family).

Each subdirectory under ``mcp_gouv_fr.apis`` is a self-contained package
(models, HTTP helpers, optional config) that exposes a ``build_subserver()``
function returning a ``FastMCP`` instance.

Register APIs in :func:`default_api_mounts` / the internal registry so the root server mounts them
with a namespace prefix (e.g. ``datagouv_search_datasets``).

New API packages must follow AGENTS.md: documented tools, models, and every model field
(``Field(description=...)``) for agent discovery.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Sequence

from fastmcp import FastMCP

type ApiMount = tuple[str, Callable[[], FastMCP]]

type _RegistryEntry = tuple[str, Callable[[], FastMCP], str | None]

_logger = logging.getLogger(__name__)


def _api_registry() -> tuple[_RegistryEntry, ...]:
    """(api_id, subserver_factory, env_var_to_warn_if_missing_when_loaded)."""
    from mcp_gouv_fr.apis.datagouv.server import build_subserver as build_datagouv
    from mcp_gouv_fr.apis.geo.server import build_subserver as build_geo
    from mcp_gouv_fr.apis.insee.server import build_subserver as build_insee
    from mcp_gouv_fr.apis.radiofrance.server import build_subserver as build_radiofrance

    return (
        ("datagouv", build_datagouv, None),
        ("geo", build_geo, None),
        ("insee", build_insee, "MCP_GOUV_INSEE_API_KEY"),
        ("radiofrance", build_radiofrance, "MCP_GOUV_RADIOFRANCE_API_TOKEN"),
    )


def registered_api_ids() -> tuple[str, ...]:
    """Stable ordered list of API identifiers accepted by :func:`resolve_api_mounts`."""
    return tuple(r[0] for r in _api_registry())


def default_api_mounts() -> Sequence[ApiMount]:
    """Ordered list of (namespace, subserver_factory) for the composite MCP server (all APIs)."""
    result = tuple((ns, fac) for ns, fac, _ in _api_registry())
    _logger.info("default_api_mounts: %s", [ns for ns, _ in result])
    return result


def resolve_api_mounts(api_ids: Sequence[str] | None) -> list[ApiMount]:
    """Resolve which API packages to mount.

    ``None`` or an empty sequence loads **all** registered APIs (registry order).
    Otherwise ``api_ids`` is a list of API identifiers; order is preserved.
    Unknown ids raise ``ValueError``.
    """
    registry = _api_registry()
    by_id: dict[str, _RegistryEntry] = {r[0]: r for r in registry}

    if not api_ids:
        all_mounts = [(ns, fac) for ns, fac, _ in registry]
        _logger.info("resolve_api_mounts: loading all APIs %s", [ns for ns, _ in all_mounts])
        return all_mounts

    mounts: list[ApiMount] = []
    for raw in api_ids:
        api_id = raw.strip()
        if not api_id:
            continue
        entry = by_id.get(api_id)
        if entry is None:
            known = ", ".join(by_id)
            raise ValueError(f"unknown API {api_id!r}; known: {known}")
        mounts.append((entry[0], entry[1]))
    if not mounts:
        all_mounts = [(ns, fac) for ns, fac, _ in registry]
        _logger.warning(
            "resolve_api_mounts: no valid API ids after parsing; falling back to all %s",
            [ns for ns, _ in all_mounts],
        )
        return all_mounts
    _logger.info("resolve_api_mounts: selected APIs %s", [ns for ns, _ in mounts])
    return mounts


def warn_if_missing_api_keys(loaded_api_ids: Sequence[str]) -> None:
    """Log a warning for each loaded API that expects a key when the env var is unset."""
    key_by_id = {r[0]: r[2] for r in _api_registry()}
    for api_id in loaded_api_ids:
        env_name = key_by_id.get(api_id)
        if env_name and not os.environ.get(env_name):
            _logger.warning(
                "API %r is enabled but %s is not set; calls that require this credential may fail.",
                api_id,
                env_name,
            )
