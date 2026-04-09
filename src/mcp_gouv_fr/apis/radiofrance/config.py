"""Radio France Open API settings (GraphQL).

See https://developers.radiofrance.fr/ for signup, terms, and schema exploration.
"""

from __future__ import annotations

import os

# Default matches public documentation (POST + x-token).
RADIOFRANCE_GRAPHQL_URL = os.environ.get(
    "MCP_GOUV_RADIOFRANCE_GRAPHQL_URL",
    "https://openapi.radiofrance.fr/v1/graphql",
)

RADIOFRANCE_API_TOKEN = os.environ.get("MCP_GOUV_RADIOFRANCE_API_TOKEN", "").strip()
