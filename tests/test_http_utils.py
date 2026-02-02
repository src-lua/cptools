"""
Tests for lib/http_utils.py - HTTP request utilities.
"""
import json
import urllib.error
from unittest.mock import patch, MagicMock
import pytest
from lib.http_utils import fetch_url, fetch_json

def test_fetch_url_success():
    """Test successful URL fetch."""
    with patch('lib.http_utils.urlopen') as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>content</html>"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        content = fetch_url("http://example.com")
        assert content == "<html>content</html>"

def test_fetch_url_failure():
    """Test URL fetch failure."""
    with patch('lib.http_utils.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.URLError("Network error")
        
        with pytest.raises(Exception):
            fetch_url("http://example.com")

def test_fetch_json_success():
    """Test successful JSON fetch."""
    expected = {"status": "OK", "result": []}
    with patch('lib.http_utils.fetch_url') as mock_fetch:
        mock_fetch.return_value = json.dumps(expected)
        
        result = fetch_json("http://api.example.com")
        assert result == expected

def test_fetch_json_failure():
    """Test JSON fetch failure (invalid JSON)."""
    with patch('lib.http_utils.fetch_url') as mock_fetch:
        mock_fetch.return_value = "Not JSON"
        
        with pytest.raises(Exception):
            fetch_json("http://api.example.com")