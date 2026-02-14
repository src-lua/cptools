"""
HTTP utilities for fetching web content with consistent headers.

This module centralizes HTTP requests to ensure consistent User-Agent
and other headers across all platform APIs. Supports cookie-based
authentication for private/group content.
"""
import json
from urllib.request import Request, urlopen, HTTPCookieProcessor, build_opener
from urllib.error import URLError, HTTPError
from typing import Optional
import http.cookiejar


# Standard headers used across all HTTP requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def fetch_url(url, timeout=15, headers=None, cookies=None):
    """
    Fetch content from URL with standard headers.

    Args:
        url: URL to fetch
        timeout: Timeout in seconds (default: 15)
        headers: Additional headers to merge with defaults (optional)
        cookies: CookieJar or dict of cookies to include (optional)

    Returns:
        Response text decoded as UTF-8

    Raises:
        PlatformError: On network errors or HTTP errors

    Examples:
        >>> content = fetch_url("https://example.com")
        >>> content = fetch_url("https://api.example.com", timeout=10)
        >>> content = fetch_url("https://private.com", cookies=cookie_jar)
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

        # Handle cookies
        if cookies:
            opener = _build_opener_with_cookies(cookies)
            with opener.open(req, timeout=timeout) as response:
                return response.read().decode('utf-8')
        else:
            with urlopen(req, timeout=timeout) as response:
                return response.read().decode('utf-8')

    except HTTPError as e:
        raise PlatformError(f"HTTP error {e.code} fetching {url}: {e.reason}") from e
    except URLError as e:
        raise PlatformError(f"Network error fetching {url}: {e.reason}") from e
    except Exception as e:
        raise PlatformError(f"Unexpected error fetching {url}: {e}") from e


def _build_opener_with_cookies(cookies):
    """Build URL opener with cookie support."""
    if isinstance(cookies, dict):
        # Convert dict to CookieJar
        jar = http.cookiejar.CookieJar()
        for name, value in cookies.items():
            cookie = http.cookiejar.Cookie(
                version=0, name=name, value=value,
                port=None, port_specified=False,
                domain='', domain_specified=False, domain_initial_dot=False,
                path='/', path_specified=True,
                secure=True, expires=None, discard=True,
                comment=None, comment_url=None,
                rest={}, rfc2109=False
            )
            jar.set_cookie(cookie)
        cookies = jar

    processor = HTTPCookieProcessor(cookies)
    return build_opener(processor)


def fetch_json(url, timeout=10, headers=None, cookies=None):
    """
    Fetch and parse JSON from URL.

    Args:
        url: URL to fetch
        timeout: Timeout in seconds (default: 10)
        headers: Additional headers (optional)
        cookies: CookieJar or dict of cookies (optional)

    Returns:
        Parsed JSON as dict/list

    Raises:
        PlatformError: On network errors or JSON parsing errors

    Examples:
        >>> data = fetch_json("https://api.example.com/data")
    """
    from . import PlatformError

    try:
        content = fetch_url(url, timeout, headers, cookies)
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise PlatformError(f"Invalid JSON response from {url}: {e}") from e
    except PlatformError:
        # Re-raise PlatformError from fetch_url
        raise


def fetch_url_with_auth(url, timeout=15, headers=None, domain=None, force_refresh=False):
    """
    Fetch URL with automatic browser cookie authentication.

    This is a convenience wrapper that automatically extracts and uses
    browser cookies for the given domain.

    Args:
        url: URL to fetch
        timeout: Timeout in seconds
        headers: Additional headers
        domain: Domain to extract cookies for (auto-detected from URL if None)
        force_refresh: Force cookie re-extraction from browser (ignore cache)

    Returns:
        Response text decoded as UTF-8
    """
    from .cookies import get_cookie_extractor
    from urllib.parse import urlparse

    if domain is None:
        parsed = urlparse(url)
        domain = parsed.netloc

    extractor = get_cookie_extractor()
    cookies = extractor.extract_cookies(domain, force_refresh=force_refresh)

    return fetch_url(url, timeout, headers, cookies)
