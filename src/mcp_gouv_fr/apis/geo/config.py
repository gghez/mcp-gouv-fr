"""geo.api.gouv.fr-specific settings."""

from __future__ import annotations

import os

GEO_API_BASE = os.environ.get(
    "MCP_GOUV_GEO_API_BASE",
    "https://geo.api.gouv.fr",
)
