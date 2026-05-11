# Registering the MCP Server in Claude Code

This guide assumes you already have the server running in SSE mode.  
If not, follow [RUN.md](RUN.md) first.

**MCP endpoint:** `http://localhost:8000/sse`  
(adjust host/port if you changed the defaults)

---

## Option A — Claude Code CLI (recommended)

Run this once from any terminal:

```bash
claude mcp add --transport sse databricks http://localhost:8000/sse
```

Claude Code writes the entry to your **user-level** settings (`~/.claude/settings.json`) so it is available in every project.

Verify it was added:

```bash
claude mcp list
```

You should see `databricks` in the output.

---

## Option B — Project settings file

Add the server to `.claude/settings.json` in the repo root so any team member who opens this project gets it automatically.

```json
{
  "mcpServers": {
    "databricks": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

> The server must already be running before Claude Code is opened. Claude Code connects to the URL on startup — it does **not** launch the process for you in SSE mode.

---

## Option C — Global settings file

Edit `~/.claude/settings.json` manually and add the same block as Option B under `mcpServers`.

---

## Verifying the connection

Start (or restart) Claude Code from the project directory:

```bash
claude
```

Then run:

```
/mcp
```

You should see `databricks` listed as a connected server with all its tools.

---

## Test it with a prompt

```
List all my Databricks clusters.
```

```
Upload the following Python file to /Users/victor.rijks@delaware.pro/test.py:
print("hello from MCP")
```

```
List notebooks in /Users/victor.rijks@delaware.pro
```

---

## Available tools

| Tool | Description |
|---|---|
| `list_clusters` | List all Databricks clusters |
| `create_cluster` | Create a new cluster |
| `terminate_cluster` | Terminate a cluster |
| `get_cluster` | Get cluster details |
| `start_cluster` | Start a terminated cluster |
| `list_jobs` | List all jobs |
| `run_job` | Run a job |
| `list_notebooks` | List notebooks in a workspace path |
| `export_notebook` | Export a notebook (SOURCE / JUPYTER / DBC / HTML) |
| `upload_workspace_file` | Upload any file to the workspace |
| `list_files` | List files in a DBFS path |
| `execute_sql` | Execute a SQL statement via a SQL warehouse |

---

## Troubleshooting

**`databricks` not listed in `/mcp`**  
Make sure the server is running (`Invoke-WebRequest http://localhost:8000/sse` returns 200) before starting Claude Code.

**`Connection refused` on startup**  
The server process stopped or never started. Check `databricks_mcp.log` for errors.

**Tool returns `{"error": "..."}`**  
The server reached Databricks but the API call failed. Common causes:
- `DATABRICKS_TOKEN` is expired — generate a new PAT in the Databricks UI.
- `DATABRICKS_HOST` is wrong — must include the `https://` scheme.

**Remove the registration**

```bash
claude mcp remove databricks
```

Or delete the `databricks` key from whichever settings file you edited.
