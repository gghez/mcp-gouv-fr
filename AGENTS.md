# AGENTS.md — context for AI assistants and contributors

This file summarizes the **stack**, **architecture choices**, and **conventions** for evolving `mcp-gouv-fr`.

## Stack

| Piece | Choice |
|-------|--------|
| Language | Python **3.14** |
| Packaging / lockfile | **uv** (`pyproject.toml`, `uv.lock`) |
| MCP server | **FastMCP** 3.x (official MCP Python SDK underneath) |
| Schemas / tool outputs | **Pydantic v2** (`BaseModel`, explicit output types per tool) |
| HTTP client | **httpx** **async** (`AsyncClient`) |
| Tests | **pytest** + **pytest-asyncio** (`asyncio_mode = auto`) |
| Lint | **ruff** (target `py314` in `pyproject.toml`) |
| Git hooks | **pre-commit** with **`ruff check`** (`.pre-commit-config.yaml`) |

## MCP transports

- **stdio**: default for local integrations (Claude Desktop, Cursor). No listening port; the host process spawns the server.
- **streamable-http**: for network access; FastMCP serves HTTP (Uvicorn). Prefer this over legacy SSE for new HTTP deployments when the client supports it.

CLI entrypoint: `mcp_gouv_fr.cli:main` (console script `mcp-gouv-fr`).

## Code style

- Use **async/await** for network I/O and for MCP tools that call APIs.
- **Composite server**: `mcp_gouv_fr.server.build_server()` only mounts API packages; it has no tools of its own. Each package under `apis/<name>/` exposes `build_subserver()` with its own **lifespan** (e.g. a dedicated `httpx.AsyncClient` in `apis/<name>/server.py`) and tools use `Context.lifespan_context` — avoid ad hoc globals.
- **Configuration**: shared HTTP defaults in `mcp_gouv_fr/config.py`; API-specific bases and flags in `apis/<name>/config.py` (or similar) with a clear `MCP_GOUV_*` env naming pattern.
- **Tool contracts**: simple top-level parameters; **English** docstrings and sub-server `instructions`. Short tool names inside the API package (e.g. `search_datasets`); the **namespace** adds the prefix exposed to clients (`datagouv_search_datasets`).
- **Tool outputs**: **Pydantic models** live next to the API (`apis/<name>/models.py`). Map raw API JSON via `from_api_payload` when needed. Use `model_config = ConfigDict(extra="ignore")` to tolerate API additions.

## Agent-facing documentation (required)

Agents discover behavior from MCP metadata and JSON Schemas. **Everything they consume must be self-explanatory:**

1. **Tools** — Clear `"""docstring"""` on each `@mcp.tool` function: purpose, when to use it, semantics of each argument (`Args:`), and any limits (pagination, caps). Root and sub-server `instructions` should remind agents to read these.
2. **Pydantic models** — Every output `BaseModel` needs a class docstring summarizing what the object represents and how it relates to the upstream API.
3. **Model fields** — Every field must have an explicit **`Field(..., description="...")`** (or equivalent) stating meaning, format, nullability, and links to other fields when useful (e.g. “use with `page` for pagination”). Nested models repeat the same rule.

This keeps `outputSchema` / tool descriptions sufficient for discovery without reading implementation code.

## MCP practices (short list)

1. **Single responsibility**: this repo targets French public open data; avoid unrelated integrations here.
2. **Outcome-oriented tools**: expose what agents need (search, detail, filters), not every upstream REST path.
3. **Explicit contracts**: typed parameters and Pydantic output models; document pagination and practical limits.
4. **Security**: validate inputs; no secrets in the repo; for public HTTP, add auth per [FastMCP auth](https://gofastmcp.com/servers/auth/authentication).
5. **Resilience**: timeouts, clear HTTP error behavior (`raise_for_status` in the client layer).
6. **Observability**: useful logs without leaking personal data; health routes for orchestrated HTTP deployments when needed.

## Repository layout

```
src/mcp_gouv_fr/
  __init__.py
  __main__.py
  cli.py
  config.py              # shared HTTP timeout, User-Agent
  server.py              # build_server(); mounts all APIs
  apis/
    __init__.py          # ApiMount, default_api_mounts()
    <api_name>/
      __init__.py
      config.py          # optional: API base URL, feature flags
      http.py            # thin httpx calls (or split by resource)
      models.py          # Pydantic outputs for this API's tools
      server.py          # build_subserver() -> FastMCP with @mcp.tool
      tests/             # tests for this API package (sibling of http.py, models.py, …)
        test_http.py
        test_models.py
  tests/                 # tests for package-level modules (server.py, etc.)
    test_server.py
```

Register new APIs in `default_api_mounts()` **in dependency order** if one day an API depends on another’s setup (today order only affects tool listing / resolution). For tests, `build_server(api_mounts=())` mounts nothing; `build_server(api_mounts=[...])` overrides the default list (**note**: pass `None` for the default, not `or`-combined with `()`).

## Tests

- Use a nested **`tests`** package **next to the code under test** inside `src/mcp_gouv_fr/`: e.g. **`mcp_gouv_fr/apis/<api>/tests/`** for that API’s `http.py`, `models.py`, etc., and **`mcp_gouv_fr/tests/`** for top-level modules like `server.py`. Pytest collects from `testpaths = ["src/mcp_gouv_fr"]`.
- Unit-test HTTP helpers with **`httpx.MockTransport`** (no live network in CI by default).
- Unit-test Pydantic mapping (`from_api_payload`) with representative JSON fixtures.
- Smoke-test: build the server and assert registered tool names.

## Possible extensions

- MCP **resources** for canonical dataset URLs.
- More tools (organizations, reuses, other public APIs) after checking terms of use.
- Hardened **HTTP** profile: narrow CORS, middleware, authentication.

