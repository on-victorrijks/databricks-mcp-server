"""
Tests for the notebooks API, including workspace file import.
"""

import base64
from unittest.mock import patch

import pytest

from src.api import notebooks


@pytest.mark.anyio
async def test_import_file_encodes_content():
    """Test that import_file base64-encodes the raw content before posting."""
    raw_content = "print('hello world')"
    expected_encoded = base64.b64encode(raw_content.encode("utf-8")).decode("utf-8")

    with patch("src.api.notebooks.make_api_request") as mock_request:
        mock_request.return_value = {}
        await notebooks.import_file(
            path="/Users/user@example.com/hello.py",
            content=raw_content,
        )

    posted_data = mock_request.call_args[1]["data"]
    assert posted_data["content"] == expected_encoded


@pytest.mark.anyio
async def test_import_file_default_format_is_auto():
    """Test that the default format is AUTO when not specified."""
    with patch("src.api.notebooks.make_api_request") as mock_request:
        mock_request.return_value = {}
        await notebooks.import_file(
            path="/Users/user@example.com/data.csv",
            content="col1,col2\n1,2",
        )

    posted_data = mock_request.call_args[1]["data"]
    assert posted_data["format"] == "AUTO"


@pytest.mark.anyio
async def test_import_file_passes_overwrite_flag():
    """Test that overwrite=True is forwarded to the API payload."""
    with patch("src.api.notebooks.make_api_request") as mock_request:
        mock_request.return_value = {}
        await notebooks.import_file(
            path="/Users/user@example.com/script.py",
            content="# existing file",
            overwrite=True,
        )

    posted_data = mock_request.call_args[1]["data"]
    assert posted_data["overwrite"] is True


@pytest.mark.anyio
async def test_import_file_includes_language_when_provided():
    """Test that language is included in the payload when specified."""
    with patch("src.api.notebooks.make_api_request") as mock_request:
        mock_request.return_value = {}
        await notebooks.import_file(
            path="/Users/user@example.com/notebook",
            content="# Databricks notebook source",
            format="SOURCE",
            language="PYTHON",
        )

    posted_data = mock_request.call_args[1]["data"]
    assert posted_data["language"] == "PYTHON"
    assert posted_data["format"] == "SOURCE"


@pytest.mark.anyio
async def test_import_file_omits_language_when_not_provided():
    """Test that language key is absent from the payload when not specified."""
    with patch("src.api.notebooks.make_api_request") as mock_request:
        mock_request.return_value = {}
        await notebooks.import_file(
            path="/Users/user@example.com/report.html",
            content="<html></html>",
            format="HTML",
        )

    posted_data = mock_request.call_args[1]["data"]
    assert "language" not in posted_data


@pytest.mark.anyio
async def test_import_file_calls_correct_endpoint():
    """Test that import_file posts to /api/2.0/workspace/import."""
    with patch("src.api.notebooks.make_api_request") as mock_request:
        mock_request.return_value = {}
        await notebooks.import_file(
            path="/Shared/myfile.py",
            content="x = 1",
        )

    method, endpoint = mock_request.call_args[0][0], mock_request.call_args[0][1]
    assert method == "POST"
    assert endpoint == "/api/2.0/workspace/import"
