# mcp-gouv-fr

A Python [MCP](https://modelcontextprotocol.io/) (Model Context Protocol) server built with **[FastMCP](https://gofastmcp.com/)** so assistants (Claude, Cursor, etc.) can use **French public open data** APIs, including **[data.gouv.fr](https://www.data.gouv.fr/)** and **[INSEE API Sirene](https://portail-api.insee.fr/)** (business registry lookups with a portal key).

Tool responses are typed with **Pydantic** models so clients get stable JSON schemas for structured results.

## API packages (namespaced tools)

Each government API (or portal) lives in its own Python package under `src/mcp_gouv_fr/apis/<name>/`. The root server **mounts** each package with a FastMCP **namespace**, so tool names become `namespace_tool` (e.g. `datagouv_search_datasets`, `datagouv_get_dataset`).

To add an API: create `apis/<myapi>/` with `build_subserver()` returning a `FastMCP` instance, then register `("myapi", build_subserver)` in `mcp_gouv_fr.apis.default_api_mounts`.

## Goals

- Provide **documented, outcome-oriented tools** to discover and read **dataset metadata** (and resource links), not a blind 1:1 mirror of every government API.
- Keep the server **stateless** where possible, with bounded outbound HTTP (timeouts, explicit `User-Agent`).
- Grow into other portals or public APIs while keeping a **clear scope** per domain (MCP best practice: small toolsets, simple inputs).
- Keep **tools, Pydantic models, and every model field documented** (docstrings + `Field(description=...)`) so agents can infer semantics from schemas and descriptions alone.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- **Python 3.14** (see `.python-version`)

## Install

```bash
cd mcp-gouv-fr
uv sync
```

## Run

### stdio (default — Claude Desktop, Cursor)

```bash
uv run mcp-gouv-fr
```

Explicit:

```bash
uv run mcp-gouv-fr --transport stdio
```

### Streamable HTTP

Recommended by FastMCP for network access:

```bash
uv run mcp-gouv-fr --transport streamable-http --host 127.0.0.1 --port 8765 --path /mcp
```

The MCP endpoint is then like `http://127.0.0.1:8765/mcp` (depends on `--path`).

Optional environment variables: `MCP_GOUV_TRANSPORT`, `MCP_GOUV_HOST`, `MCP_GOUV_PORT`, `MCP_GOUV_HTTP_PATH`.

## Claude Desktop (stdio)

Typical MCP config path on Windows: `%APPDATA%\Claude\claude_desktop_config.json`.

Example if the repo lives at `C:\Users\YOU\workspace\src\mcp-gouv-fr`:

```json
{
  "mcpServers": {
    "mcp-gouv-fr": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\Users\\YOU\\workspace\\src\\mcp-gouv-fr",
        "mcp-gouv-fr"
      ]
    }
  }
}
```

Adjust `--directory` to your checkout. Restart Claude Desktop after changes.

If the app does not see `uv` on `PATH`, set `command` to the full path of `uv.exe`.

## Cursor (stdio)

In Cursor MCP settings, add a server with:

- **Command**: `uv`
- **Args**: `run`, `--directory`, `PATH\TO\mcp-gouv-fr`, `mcp-gouv-fr`

Or edit the MCP servers JSON (per Cursor version/docs) to match the Claude example above.

For a **remote HTTP** MCP server, use the URL from `--transport streamable-http` if your client supports it (often with auth; see [FastMCP HTTP deployment](https://gofastmcp.com/deployment/http)).

## Environment variables (API)


| Variable                          | Description                                                                 |
| --------------------------------- | --------------------------------------------------------------------------- |
| `MCP_GOUV_DATAGOUV_API_BASE`      | data.gouv API base (default: `https://www.data.gouv.fr/api/1`)              |
| `MCP_GOUV_INSEE_API_KEY`          | INSEE portal API key (required for Sirene tools; from portail-api.insee.fr) |
| `MCP_GOUV_INSEE_SIRENE_API_BASE`  | Sirene 3.11 base (default: `https://api.insee.fr/api-sirene/3.11`)          |
| `MCP_GOUV_HTTP_TIMEOUT`           | HTTP timeout in seconds (default: `30`)                                     |
| `MCP_GOUV_USER_AGENT`             | Outbound `User-Agent` header                                                |

### INSEE Sirene (API key required)

Unlike the data.gouv integration, **Sirene lookups will not work until you set an API key.** Subscribe to the Sirene API on the [INSEE developer portal](https://portail-api.insee.fr/), generate a consumer key, and expose it to the MCP process as **`MCP_GOUV_INSEE_API_KEY`**. The server sends it as the `X-INSEE-Api-Key-Integration` header to `api.insee.fr`. If this variable is missing or empty, the `insee_*` tools return an error that asks you to configure it.

When using Claude Desktop or Cursor, add `MCP_GOUV_INSEE_API_KEY` to the server’s environment (e.g. `env` in the MCP JSON config) so the subprocess inherits it.

## Development

Tests live in nested `**tests`** packages **beside the code they exercise** under `src/mcp_gouv_fr/` (e.g. `mcp_gouv_fr/apis/datagouv/tests/` next to `http.py` / `models.py`, and `mcp_gouv_fr/tests/` for `server.py`).

```bash
uv run pytest
uv run ruff check src
```

## License

Not set yet (no `LICENSE` file in this repo).