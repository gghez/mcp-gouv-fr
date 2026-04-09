# mcp-gouv-fr

[MCP](https://modelcontextprotocol.io/) (Model Context Protocol) server built with [FastMCP](https://gofastmcp.com/) so assistants (Claude Desktop, Cursor, etc.) can query **French public open data** through documented, structured tools. Integrated APIs include **[data.gouv.fr](https://www.data.gouv.fr/)** (API v1), the national geographic referential **[geo.api.gouv.fr](https://geo.api.gouv.fr/)**, **[INSEE API Sirene](https://portail-api.insee.fr/)** for business registry lookups (portal API key required), and the **[Radio France Open API](https://developers.radiofrance.fr/)** (GraphQL, token required).

**Source repository:** [github.com/gghez/mcp-gouv-fr](https://github.com/gghez/mcp-gouv-fr)

## What it provides (technical / functional)

- **Transport:** stdio (default, for local MCP clients) or streamable HTTP (optional, for remote access where your client supports it).
- **Architecture:** one FastMCP sub-server per API family, **mounted with a namespace**. Tool names are prefixed (e.g. `datagouv_search_datasets`, `geo_search_communes`, `insee_get_unite_legale`, `radiofrance_graphql`).
- **Outputs:** [Pydantic](https://docs.pydantic.dev/) models with field descriptions, exposed to clients as JSON Schema so agents can interpret results without guessing.
- **HTTP:** stateless calls to public APIs with configurable timeout and `User-Agent`.

### Tools (current)

| MCP tool | Role |
| -------- | ---- |
| `datagouv_search_datasets` | Full-text search over datasets (title, description, organization), with pagination (`page`, `page_size`). |
| `datagouv_get_dataset` | Full metadata and **resource links** (files, APIs, formats, MIME) for one dataset, by id or slug. |
| `radiofrance_graphql` | Execute a GraphQL query against Radio France public data. Requires a Radio France Open API token (`x-token`). |
| `geo_search_communes` | Search communes by name, postal code, and/or department (at least one filter required). |
| `geo_get_commune` | Commune detail by INSEE municipality code. |
| `geo_search_departements` / `geo_get_departement` | List or search departments; detail by department code. |
| `geo_search_regions` / `geo_get_region` | List or search regions; detail by region code. |
| `insee_get_unite_legale` | Legal unit (unité légale) by 9-digit **SIREN**; requires `MCP_GOUV_INSEE_API_KEY`. |
| `insee_get_etablissement` | Establishment (établissement) by 14-digit **SIRET**; requires `MCP_GOUV_INSEE_API_KEY`. |

Additional portals may be added later as new namespaces under `mcp_gouv_fr.apis`.

## Prerequisites

- **[uv](https://docs.astral.sh/uv/)** installed and available on your `PATH` (so `uvx` works).
- This project targets **Python 3.14** (`requires-python` in `pyproject.toml`). uv will provision a compatible interpreter when installing from Git or from a local checkout.

## Recommended setup: MCP config with `uvx` (GitHub)

[`uvx`](https://docs.astral.sh/uv/guides/tools/) runs the published console script `mcp-gouv-fr` in an isolated environment. You can point it at this repository with `--from` and a **Git URL** (no manual clone required).

**Command shape:**

```bash
uvx --from git+https://github.com/gghez/mcp-gouv-fr.git mcp-gouv-fr
```

Optional: pin a branch, tag, or commit after `@` in the URL (see [uv tools guide](https://docs.astral.sh/uv/guides/tools/)), for example `git+https://github.com/gghez/mcp-gouv-fr.git@v0.1.0`.

### Claude Desktop (`claude_desktop_config.json`)

Typical path on Windows: `%APPDATA%\Claude\claude_desktop_config.json`.

```json
{
  "mcpServers": {
    "mcp-gouv-fr": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/gghez/mcp-gouv-fr.git",
        "mcp-gouv-fr"
      ]
    }
  }
}
```

Restart Claude Desktop after editing. If `uvx` is not found, use the full path to the `uv` executable and run `uv tool run` instead of `uvx`, or add uv to your user `PATH`.

### Cursor and other editors

Use the same JSON shape in your MCP servers configuration: **command** `uvx`, **args** as above. For stdio, do not pass extra arguments unless you need non-default transport (see below).

### If `uvx` is not on `PATH` (Windows)

Use the full path to `uv.exe` and the equivalent invocation:

```json
{
  "mcpServers": {
    "mcp-gouv-fr": {
      "command": "C:\\Users\\YOU\\AppData\\Local\\Programs\\uv\\uv.exe",
      "args": [
        "tool",
        "run",
        "--from",
        "git+https://github.com/gghez/mcp-gouv-fr.git",
        "mcp-gouv-fr"
      ]
    }
  }
}
```

Adjust the `command` path to match your uv installation.

## Alternative: clone the repo and run with `uv`

For a fixed checkout or local changes:

```bash
git clone https://github.com/gghez/mcp-gouv-fr.git
cd mcp-gouv-fr
uv sync
uv run mcp-gouv-fr
```

**MCP JSON (stdio)** — set `--directory` to your clone:

```json
{
  "mcpServers": {
    "mcp-gouv-fr": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\path\\to\\mcp-gouv-fr",
        "mcp-gouv-fr"
      ]
    }
  }
}
```

## Transports and CLI options

Default is **stdio** (suitable for Claude Desktop and Cursor).

```bash
uvx --from git+https://github.com/gghez/mcp-gouv-fr.git mcp-gouv-fr --transport stdio
```

**Streamable HTTP** (bind address, port, path can be changed):

```bash
uvx --from git+https://github.com/gghez/mcp-gouv-fr.git mcp-gouv-fr --transport streamable-http --host 127.0.0.1 --port 8765 --path /mcp
```

Environment variables (optional): `MCP_GOUV_TRANSPORT`, `MCP_GOUV_HOST`, `MCP_GOUV_PORT`, `MCP_GOUV_HTTP_PATH`, `MCP_GOUV_APIS` (comma-separated API ids; default: all).

## Environment variables (API behavior)

| Variable | Description |
| -------- | ----------- |
| `MCP_GOUV_APIS` | Comma-separated API ids to load (`datagouv`, `geo`, `insee`, `radiofrance`); default is all |
| `MCP_GOUV_DATAGOUV_API_BASE` | data.gouv API base URL (default: `https://www.data.gouv.fr/api/1`) |
| `MCP_GOUV_GEO_API_BASE` | Geo API base URL (default: `https://geo.api.gouv.fr`) |
| `MCP_GOUV_INSEE_API_KEY` | INSEE portal consumer key for Sirene (**required** for `insee_*` tools; from [portail-api.insee.fr](https://portail-api.insee.fr/)) |
| `MCP_GOUV_INSEE_SIRENE_API_BASE` | Sirene 3.11 API base (default: `https://api.insee.fr/api-sirene/3.11`) |
| `MCP_GOUV_RADIOFRANCE_GRAPHQL_URL` | Radio France GraphQL endpoint (default: `https://openapi.radiofrance.fr/v1/graphql`) |
| `MCP_GOUV_RADIOFRANCE_API_TOKEN` | Radio France Open API key (`x-token`); required for `radiofrance_graphql` ([portal](https://developers.radiofrance.fr/)) |
| `MCP_GOUV_HTTP_TIMEOUT` | Outbound HTTP timeout in seconds (default: `30`) |
| `MCP_GOUV_USER_AGENT` | `User-Agent` header for HTTP requests |

In MCP JSON, set these under `env` next to `command` / `args` if your client supports it.

### INSEE Sirene (API key required)

Unlike data.gouv and geo.api.gouv.fr, **Sirene lookups will not work until you set an API key.** Subscribe to the Sirene API on the [INSEE developer portal](https://portail-api.insee.fr/), generate a consumer key, and expose it to the MCP process as **`MCP_GOUV_INSEE_API_KEY`**. The server sends it as the `X-INSEE-Api-Key-Integration` header to `api.insee.fr`. If this variable is missing or empty, the `insee_*` tools return an error that asks you to configure it.

When using Claude Desktop or Cursor, add `MCP_GOUV_INSEE_API_KEY` to the server’s environment (e.g. `env` in the MCP JSON config) so the subprocess inherits it.

## Development

Contributors: tests and lint live in the repo; run `uv run pytest` and `uv run ruff check src`. See `AGENTS.md` for layout conventions (nested `tests` next to the code they cover).

## License

Not set yet (no `LICENSE` file in this repository).
