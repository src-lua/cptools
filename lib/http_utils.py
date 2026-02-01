"""
HTTP utilities for fetching web content with consistent headers.

This module centralizes HTTP requests to ensure consistent User-Agent
and other headers across all platform APIs.
"""
import json
from urllib.request import Request, urlopen
from urllib.error import URLError


# Standard headers used across all HTTP requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def fetch_url(url, timeout=15, headers=None):
    """
    Fetch content from URL with standard headers.

    Args:
        url: URL to fetch
        timeout: Timeout in seconds (default: 15)
        headers: Additional headers to merge with defaults (optional)

    Returns:
        Response text decoded as UTF-8

    Raises:
        URLError: On network errors or HTTP errors

    Examples:
        >>> content = fetch_url("https://example.com")
        >>> content = fetch_url("https://api.example.com", timeout=10)
    """
    req = Request(url)

    # Apply default headers
    final_headers = DEFAULT_HEADERS.copy()
    if headers:
        final_headers.update(headers)

    for key, value in final_headers.items():
        req.add_header(key, value)

    with urlopen(req, timeout=timeout) as response:
        return response.read().decode('utf-8')


def fetch_json(url, timeout=10, headers=None):
    """
    Fetch and parse JSON from URL.

    Args:
        url: URL to fetch
        timeout: Timeout in seconds (default: 10)
        headers: Additional headers (optional)

    Returns:
        Parsed JSON as dict/list

    Raises:
        URLError: On network errors
        json.JSONDecodeError: If response is not valid JSON

    Examples:
        >>> data = fetch_json("https://api.example.com/data")
    """
    content = fetch_url(url, timeout, headers)
    return json.loads(content)
