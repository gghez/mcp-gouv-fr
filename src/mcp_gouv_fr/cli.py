"""CLI entrypoint: run the MCP server over stdio (default) or streamable HTTP."""

from __future__ import annotations

import argparse
import os
import sys

from mcp_gouv_fr.apis import registered_api_ids, resolve_api_mounts, warn_if_missing_api_keys
from mcp_gouv_fr.server import build_server


def _parse_apis_arg(raw: str | None) -> list[str] | None:
    """Split a comma-separated API list; ``None``/blank means load all APIs."""
    if raw is None:
        return None
    stripped = raw.strip()
    if not stripped:
        return None
    parts = [p.strip() for p in stripped.split(",") if p.strip()]
    return parts or None


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="mcp-gouv-fr",
        description="MCP server for French public open data (data.gouv.fr, geo, INSEE Sirene, …).",
    )
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default=os.environ.get("MCP_GOUV_TRANSPORT", "stdio"),
        help="MCP transport: stdio for local desktop clients, or streamable-http. "
        "Default: stdio, or MCP_GOUV_TRANSPORT.",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_GOUV_HOST", "127.0.0.1"),
        help="Bind address for streamable-http only.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MCP_GOUV_PORT", "8765")),
        help="TCP port for streamable-http only.",
    )
    parser.add_argument(
        "--path",
        default=os.environ.get("MCP_GOUV_HTTP_PATH", "/mcp"),
        help="HTTP path for the MCP endpoint (streamable-http only).",
    )
    known = ", ".join(registered_api_ids())
    parser.add_argument(
        "--apis",
        default=os.environ.get("MCP_GOUV_APIS"),
        metavar="LIST",
        help=(
            "Comma-separated API ids to load (default: all). "
            f"Known: {known}. "
            "Also settable via MCP_GOUV_APIS."
        ),
    )
    args = parser.parse_args(argv)

    try:
        mounts = resolve_api_mounts(_parse_apis_arg(args.apis))
    except ValueError as e:
        print(f"{parser.prog}: error: {e}", file=sys.stderr)
        raise SystemExit(2) from e

    loaded_ids = [ns for ns, _ in mounts]
    warn_if_missing_api_keys(loaded_ids)

    mcp = build_server(api_mounts=mounts)

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
            path=args.path,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
