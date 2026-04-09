"""CLI entrypoint: run the MCP server over stdio (default) or streamable HTTP."""

from __future__ import annotations

import argparse
import logging
import os
import sys

from mcp_gouv_fr._logging import configure_logging
from mcp_gouv_fr.apis import registered_api_ids, resolve_api_mounts, warn_if_missing_api_keys
from mcp_gouv_fr.server import build_server

_log = logging.getLogger(__name__)


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
    configure_logging()
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

    _log.info(
        "CLI starting: transport=%s host=%s port=%s path=%s apis=%r",
        args.transport,
        args.host,
        args.port,
        args.path,
        args.apis,
    )
    if args.transport == "stdio" and (
        os.environ.get("MCP_GOUV_HOST")
        or os.environ.get("MCP_GOUV_PORT")
        or os.environ.get("MCP_GOUV_HTTP_PATH")
    ):
        _log.warning(
            "Transport is stdio but MCP_GOUV_HOST / MCP_GOUV_PORT / MCP_GOUV_HTTP_PATH are set; "
            "they are ignored unless you use streamable-http.",
        )

    try:
        mounts = resolve_api_mounts(_parse_apis_arg(args.apis))
    except ValueError as e:
        _log.error("Invalid API selection: %s", e)
        print(f"{parser.prog}: error: {e}", file=sys.stderr)
        raise SystemExit(2) from e

    loaded_ids = [ns for ns, _ in mounts]
    warn_if_missing_api_keys(loaded_ids)

    try:
        mcp = build_server(api_mounts=mounts)
    except Exception:
        _log.exception("Failed to build MCP server")
        raise

    if args.transport == "stdio":
        _log.info("Running MCP over stdio")
        mcp.run(transport="stdio")
    else:
        _log.info(
            "Running MCP over streamable-http at http://%s:%s%s",
            args.host,
            args.port,
            args.path,
        )
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
        _log.info("Interrupted by user")
        sys.exit(130)
    except Exception:
        _log.exception("Fatal error in main")
        raise
