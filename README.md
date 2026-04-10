# mcp-gouv-fr

[MCP](https://modelcontextprotocol.io/) server built with [FastMCP](https://gofastmcp.com/) for **Claude Desktop**, **Cursor**, and other clients. Use it to explore **French public open data** through ready-made tools instead of calling each portal yourself.

**Source repository:** [github.com/gghez/mcp-gouv-fr](https://github.com/gghez/mcp-gouv-fr)

## APIs

| API | What you can do |
| --- | ---------------- |
| [data.gouv.fr](https://www.data.gouv.fr/) | Search and open datasets: metadata, organization, and links to files or APIs. |
| [geo.api.gouv.fr](https://geo.api.gouv.fr/) | Look up communes, departments, and regions (names, codes, and related geography). |
| [INSEE API Sirene](https://portail-api.insee.fr/) | Look up a legal entity (**SIREN**) or an establishment (**SIRET**); needs an INSEE API key. |
| [Radio France Open API](https://developers.radiofrance.fr/) | Run GraphQL queries on Radio France open data; needs an API token. |

### data.gouv.fr

Tools use the `datagouv_` prefix.

| Tool | What it does |
| --- | --- |
| `datagouv_search_datasets` | Search datasets by title, description, or organization, with pagination. |
| `datagouv_get_dataset` | Full metadata and resource links for one dataset (id or slug). |

### geo.api.gouv.fr

Tools use the `geo_` prefix.

| Tool | What it does |
| --- | --- |
| `geo_search_communes` | Search communes by name, postal code, and/or department (at least one filter). |
| `geo_get_commune` | Commune details by INSEE municipality code. |
| `geo_search_departements` | List or search departments. |
| `geo_get_departement` | Department detail by code. |
| `geo_search_regions` | List or search regions. |
| `geo_get_region` | Region detail by code. |

### INSEE API Sirene

Tools use the `insee_` prefix. Set **`MCP_GOUV_INSEE_API_KEY`** or these tools will report a configuration error.

| Tool | What it does |
| --- | --- |
| `insee_get_unite_legale` | Legal unit (unité légale) by 9-digit **SIREN**. |
| `insee_get_etablissement` | Establishment (établissement) by 14-digit **SIRET**. |

### Radio France Open API

Tools use the `radiofrance_` prefix. Set **`MCP_GOUV_RADIOFRANCE_API_TOKEN`** for `radiofrance_graphql`.

| Tool | What it does |
| --- | --- |
| `radiofrance_graphql` | Execute a GraphQL query against Radio France public data. |

Default transport is **stdio** for local MCP clients; **streamable HTTP** is optional for remote access (see [Transports and CLI options](#transports-and-cli-options)).

## Prerequisites

- **[uv](https://docs.astral.sh/uv/)** installed and available on your `PATH` (so `uvx` works).
- This project targets **Python 3.14** (`requires-python` in `pyproject.toml`). uv will provision a compatible interpreter when installing from Git or from a local checkout.
- If you use **`uvx` with a `git+https://...` URL** (recommended install-from-GitHub flow below), **[Git](https://git-scm.com/)** must be installed and **`git` must be on the `PATH` of the MCP subprocess**. uv clones or updates the repo using Git; if Git is missing you get: `Git executable not found`. On Windows, **Claude Desktop** sometimes spawns MCP servers with a shorter `PATH` than your terminal: either use the [clone + `uv run`](#alternative-clone-the-repo-and-run-with-uv) setup, or extend `PATH` in the server `env` block (see below).

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
      ],
      "env": {
        "PATHEXT": ".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC;.PY;.PYW"
      }
    }
  }
}
```

Restart Claude Desktop after editing. If `uvx` is not found, use the full path to the `uv` executable and run `uv tool run` instead of `uvx`, or add uv to your user `PATH`.

**If uv fails with “Git executable not found”** (common on Windows), the MCP host did not expose `git` on `PATH`. Fixes:

1. **System-wide (simplest):** add `C:\Program Files\Git\cmd` (or your Git install) to the **user or system** `PATH` in Windows Settings so GUI apps (Claude Desktop) inherit it, then restart Claude.
2. **Per server:** set `env.PATH` in the MCP JSON to a **single string** that lists every folder the process needs, in order — at minimum **Git’s `cmd`** and the folder containing **`uv.exe` / `uvx.exe`** (e.g. `C:\Users\YOU\.local\bin`). Some clients **replace** the process `PATH` entirely when `env` is set, so do not rely on `${PATH}` expansion unless you verified your client merges variables.
3. **Avoid Git at MCP startup:** use [clone + `uv run`](#alternative-clone-the-repo-and-run-with-uv) (`uv run --directory … mcp-gouv-fr`) after `uv sync` in that clone; uv then runs the project without cloning from Git on each start.

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

Environment variables (optional): `MCP_GOUV_TRANSPORT`, `MCP_GOUV_HOST`, `MCP_GOUV_PORT`, `MCP_GOUV_HTTP_PATH`, `MCP_GOUV_APIS` (comma-separated API ids; default: all), `MCP_GOUV_LOG_LEVEL` (logging level for stderr; default: `INFO`).

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
| `MCP_GOUV_LOG_LEVEL` | Stderr log level for the server process (`DEBUG`, `INFO`, `WARNING`, …; default: `INFO`) |

In MCP JSON, set these under `env` next to `command` / `args` if your client supports it.

### INSEE Sirene (API key required)

Unlike data.gouv and geo.api.gouv.fr, **Sirene lookups will not work until you set an API key.** Subscribe to the Sirene API on the [INSEE developer portal](https://portail-api.insee.fr/), generate a consumer key, and expose it to the MCP process as **`MCP_GOUV_INSEE_API_KEY`**. The server sends it as the `X-INSEE-Api-Key-Integration` header to `api.insee.fr`. If this variable is missing or empty, the `insee_*` tools return an error that asks you to configure it.

When using Claude Desktop or Cursor, add `MCP_GOUV_INSEE_API_KEY` to the server’s environment (e.g. `env` in the MCP JSON config) so the subprocess inherits it.

## Development

Contributors: tests and lint live in the repo. Run `uv run pytest` and `uv run ruff check src`. Install Git hooks with `uv run pre-commit install` (runs `ruff check --fix` on commit). Tool outputs use [Pydantic](https://docs.pydantic.dev/) models (JSON Schema for MCP clients). See [AGENTS.md](AGENTS.md) for layout conventions (nested `tests` next to the code they cover).

## License

Not set yet (no `LICENSE` file in this repository).
