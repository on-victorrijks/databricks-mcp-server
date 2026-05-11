# Databricks MCP Server — Development Guide

## Project Structure

```
src/server/   - MCP server implementation (*_mcp_server.py, *.py)
src/api/      - Databricks API client
src/core/     - Core utilities and shared functionality
src/cli/      - Command-line interface
tests/        - Test files (test_*.py), mirroring src/ structure
examples/     - Runnable usage examples
scripts/      - Helper scripts (.ps1, .sh)
docs/api/     - Sphinx-generated API documentation
```

Required files: `README.md`, `pyproject.toml`, `.gitignore`, `src/server/databricks_mcp_server.py`.

## Development Environment

- **Python:** >= 3.10
- **Package manager:** `uv`
- **Virtual environment:** `.venv`
- **Linters:** pylint, flake8, mypy

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS
uv pip install -e ".[dev]"

# Test
pytest tests/

# Lint
pylint src/ tests/
flake8 src/ tests/
mypy src/
```

## Python Coding Standards

### Style
- Line length: **100 characters** maximum
- Indentation: **4 spaces** (no tabs)
- Quotes: **double quotes** by default

### Naming
| Kind | Convention |
|---|---|
| Variables / functions / methods / files | `snake_case` |
| Constants | `UPPER_SNAKE_CASE` |
| Classes | `PascalCase` |

### Imports
Order: standard library → third-party → first-party, each group alphabetised.

```python
import json
import os

import requests

from src.core import utils
```

### Type Annotations
Required for all non-test code (PEP 484).

### Docstrings
Google-style required for all classes, methods, and functions:

```python
def function_name(param1: str, param2: int) -> bool:
    """One-line summary.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: When and why this exception is raised.
    """
```

## Databricks API Implementation

Apply to `src/api/**/*.py`.

### Function Design
API functions must be **async**:

```python
async def api_call(client, **params):
    """Short description of the API call.

    Args:
        client: Databricks client instance.
        **params: API-specific parameters.

    Returns:
        Processed and validated API response.

    Raises:
        APIError: When the API call fails.
    """
```

### Error Handling
Implement retry logic for transient failures and rate limiting:

```python
try:
    response = await client.make_request(...)
except RateLimitException:
    await asyncio.sleep(retry_after)
    response = await client.make_request(...)
except APIException as e:
    raise APIError(f"Failed to call {api_name}: {str(e)}")
```

### Response Validation
Validate responses against expected schema before returning; return typed objects, not raw JSON.

### Performance
- Set appropriate timeouts on all requests.
- Use bulk operations where available.
- Cache responses when appropriate.

## MCP Tool Implementation

Apply to `src/server/**/*.py`.

### Function Signature
Tool functions must be **async**:

```python
async def tool_name(params: Dict[str, Any]) -> Dict[str, Any]:
    """Tool description.

    Args:
        params: Dictionary of parameters from MCP client.

    Returns:
        Dictionary adhering to MCP protocol response format.
    """
```

### Documentation Header
Each tool requires a documentation block:

```python
"""
name: list_clusters
description: Lists all available Databricks clusters
parameters: {}
returns: List of cluster objects
"""
```

### Error Handling
Return errors as part of the result object — never raise unhandled exceptions out of a tool:

```python
{
    "result": None,
    "isError": True,
    "errorMessage": "Unable to connect to Databricks API"
}
```

### Performance
- Set timeouts on all external calls.
- Provide progress updates for long-running operations.
- Handle Databricks API rate limiting with retries.

## Documentation Standards

### Required Files
- `README.md` — project description, installation, usage examples, configuration, links to docs
- `tests/README.md`
- `examples/README.md`

### API Docs
Use Sphinx with autodoc; output to `docs/api/`.

### Examples
All examples must be runnable without modification and cover common use cases.

## Testing Standards

Apply to `tests/**/*.py`.

- **Framework:** pytest
- **Minimum coverage:** 80% (excluding `scripts/*` and `examples/*`)
- **File naming:** `test_*.py`, mirroring the `src/` directory layout

### Test Types
- **Unit:** individual functions/classes in isolation
- **Integration:** components working together
- **MCP protocol:** verifies correct MCP protocol implementation

### Best Practices
- Use fixtures and parametrised tests.
- Mock external dependencies (especially API calls).
- Keep tests fast and independent.

```python
import pytest
from unittest.mock import AsyncMock, patch

from src.api.cluster import list_clusters

@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.make_request.return_value = {"clusters": [{"cluster_id": "abc123"}]}
    return client

@pytest.mark.asyncio
async def test_list_clusters(mock_client):
    """Test that list_clusters returns expected format."""
    result = await list_clusters(mock_client)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["cluster_id"] == "abc123"
    mock_client.make_request.assert_called_once()
```

## References

- [Databricks REST API](https://docs.databricks.com/api/azure/workspace/clusters/edit)
- [MCP Protocol](https://modelcontextprotocol.io/llms-full.txt)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [PEP 8](https://peps.python.org/pep-0008/)
