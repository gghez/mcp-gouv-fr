"""CLI entrypoint: run the MCP server over stdio (default) or streamable HTTP."""

from __future__ import annotations

import argparse
import os
import sys

from mcp_gouv_fr.server import build_server


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="mcp-gouv-fr",
        description="MCP server for French public open data (data.gouv.fr).",
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
    args = parser.parse_args(argv)

    mcp = build_server()

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
