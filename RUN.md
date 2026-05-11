# Running the Databricks MCP Server

The server supports two transports:

| Transport | Use case |
|---|---|
| `stdio` | Claude Code subprocess (default, no port required) |
| `sse` | Terminal / container / remote — exposes an HTTP+SSE endpoint |

This guide covers the **SSE** mode, which lets you start the server in a terminal and connect to it from Claude Code (or any other MCP client) over the network.

---

## Prerequisites

- Python 3.13
- [`uv`](https://docs.astral.sh/uv/) — install once:

  ```powershell
  # Windows
  irm https://astral.sh/uv/install.ps1 | iex
  ```

  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## 1. Configure credentials

Copy the example env file and fill in your Databricks credentials:

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```
DATABRICKS_HOST=https://adb-<workspace-id>.<region>.azuredatabricks.net
DATABRICKS_TOKEN=dapi...
```

---

## 2. Install dependencies

```powershell
uv sync
```

> `uv sync` reads `.python-version` (pinned to 3.13) and installs all dependencies into `.venv` automatically.

---

## 3. Start the server

```powershell
uv run python -m src.server --transport sse
```

Default: binds to `0.0.0.0:8000`. You should see:

```
Databricks MCP server listening on http://0.0.0.0:8000/sse
```

### Options

| Flag | Env var | Default | Description |
|---|---|---|---|
| `--transport` | `MCP_TRANSPORT` | `stdio` | `stdio` or `sse` |
| `--host` | `MCP_HOST` | `0.0.0.0` | Bind address |
| `--port` | `MCP_PORT` | `8000` | Port number |

```powershell
# Custom port, localhost only
uv run python -m src.server --transport sse --host 127.0.0.1 --port 9000

# Or via env vars
$env:MCP_TRANSPORT = "sse"; $env:MCP_PORT = "9000"; uv run python -m src.server
```

---

## 4. Verify the server is running

```powershell
Invoke-WebRequest -Uri http://localhost:8000/sse -Method GET
```

You should get a `200 OK` response with `Content-Type: text/event-stream`.

---

## Docker / Container

A minimal `Dockerfile` for containerised deployments:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .python-version ./
COPY src/ src/

RUN pip install uv && uv sync --no-dev

ENV MCP_TRANSPORT=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "src.server"]
```

Build and run:

```bash
docker build -t databricks-mcp .
docker run -p 8000:8000 \
  -e DATABRICKS_HOST=https://adb-<id>.<region>.azuredatabricks.net \
  -e DATABRICKS_TOKEN=dapi... \
  databricks-mcp
```

---

## Logs

The server writes structured logs to `databricks_mcp.log` in the working directory. Tail them in a second terminal:

```powershell
Get-Content databricks_mcp.log -Wait
```
