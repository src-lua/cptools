"""
HTTP utilities for fetching web content with consistent headers.

This module centralizes HTTP requests to ensure consistent User-Agent
and other headers across all platform APIs.
"""
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


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
        PlatformError: On network errors or HTTP errors

    Examples:
        >>> content = fetch_url("https://example.com")
        >>> content = fetch_url("https://api.example.com", timeout=10)
    """
    # Import here to avoid circular dependency
    from . import PlatformError

    try:
        req = Request(url)

        # Apply default headers
        final_headers = DEFAULT_HEADERS.copy()
        if headers:
            final_headers.update(headers)

        for key, value in final_headers.items():
            req.add_header(key, value)

        with urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except HTTPError as e:
        raise PlatformError(f"HTTP error {e.code} fetching {url}: {e.reason}") from e
    except URLError as e:
        raise PlatformError(f"Network error fetching {url}: {e.reason}") from e
    except Exception as e:
        raise PlatformError(f"Unexpected error fetching {url}: {e}") from e


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
        PlatformError: On network errors or JSON parsing errors

    Examples:
        >>> data = fetch_json("https://api.example.com/data")
    """
    from . import PlatformError

    try:
        content = fetch_url(url, timeout, headers)
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise PlatformError(f"Invalid JSON response from {url}: {e}") from e
    except PlatformError:
        # Re-raise PlatformError from fetch_url
        raise
