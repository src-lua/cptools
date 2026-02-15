"""
Tests for lib/http_utils.py - HTTP request utilities.
"""
import json
import urllib.error
from unittest.mock import patch, MagicMock
import pytest
from cptools.lib.http_utils import fetch_url, fetch_json, fetch_url_with_auth
import http.cookiejar

def test_fetch_url_success():
    """Test successful URL fetch."""
    with patch('cptools.lib.http_utils.urlopen') as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>content</html>"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        content = fetch_url("http://example.com")
        assert content == "<html>content</html>"

def test_fetch_url_failure():
    """Test URL fetch failure."""
    with patch('cptools.lib.http_utils.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.URLError("Network error")
        
        with pytest.raises(Exception):
            fetch_url("http://example.com")

def test_fetch_json_success():
    """Test successful JSON fetch."""
    expected = {"status": "OK", "result": []}
    with patch('cptools.lib.http_utils.fetch_url') as mock_fetch:
        mock_fetch.return_value = json.dumps(expected)
        
        result = fetch_json("http://api.example.com")
        assert result == expected

def test_fetch_json_failure():
    """Test JSON fetch failure (invalid JSON)."""
    with patch('cptools.lib.http_utils.fetch_url') as mock_fetch:
        mock_fetch.return_value = "Not JSON"

        with pytest.raises(Exception):
            fetch_json("http://api.example.com")


def test_fetch_url_with_cookies():
    """Test URL fetch with cookie support."""
    jar = http.cookiejar.CookieJar()
    cookie = http.cookiejar.Cookie(
        version=0, name='session', value='abc123',
        port=None, port_specified=False,
        domain='.example.com', domain_specified=True, domain_initial_dot=True,
        path='/', path_specified=True,
        secure=True, expires=None, discard=True,
        comment=None, comment_url=None, rest={}, rfc2109=False
    )
    jar.set_cookie(cookie)

    with patch('cptools.lib.http_utils.build_opener') as mock_build_opener:
        mock_opener = MagicMock()
        mock_response = MagicMock()
        mock_response.read.return_value = b"authenticated content"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__ = MagicMock()
        mock_opener.open.return_value = mock_response
        mock_build_opener.return_value = mock_opener

        content = fetch_url("http://example.com", cookies=jar)
        assert content == "authenticated content"
        mock_build_opener.assert_called_once()


def test_fetch_url_with_auth():
    """Test convenience wrapper for authenticated fetch."""
    with patch('cptools.lib.http_utils.fetch_url') as mock_fetch, \
         patch('cptools.lib.cookies.get_cookie_extractor') as mock_extractor:

        mock_jar = MagicMock()
        mock_extractor.return_value.extract_cookies.return_value = mock_jar
        mock_fetch.return_value = "content"

        result = fetch_url_with_auth("https://codeforces.com/group/test/contest/123")

        mock_extractor.return_value.extract_cookies.assert_called_once()
        mock_fetch.assert_called_once()
        assert result == "content"