"""
Browser cookie extraction and management for authenticated requests.

This module provides utilities to extract cookies from the user's browser
for accessing private/authenticated content on competitive programming platforms.
"""
import os
import json
import time
import subprocess
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
import http.cookiejar

# External dependency
try:
    import browser_cookie3
    COOKIE_SUPPORT = True
except ImportError:
    COOKIE_SUPPORT = False


@dataclass
class CookieCache:
    """Cached cookie data with expiration."""
    cookies: Dict[str, Dict[str, str]]  # domain -> {name: value}
    extracted_at: float
    browser: str

    def is_expired(self, max_age_hours: int = 24) -> bool:
        """
        Check if cache is older than max_age_hours.

        Args:
            max_age_hours: Maximum age in hours. -1 = never expire.

        Returns:
            True if expired, False otherwise
        """
        if max_age_hours == -1:
            return False  # Never expire

        age = time.time() - self.extracted_at
        return age > (max_age_hours * 3600)


class CookieExtractor:
    """
    Extract and manage browser cookies for authenticated requests.

    Supports automatic extraction from Firefox, Chrome, Edge, Brave, etc.
    Caches cookies to avoid repeated browser database access.
    """

    CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "cptools")
    CACHE_FILE = os.path.join(CACHE_DIR, "browser_cookies.json")

    # Browser priority order (first available will be used)
    BROWSERS = ['zen', 'firefox', 'chrome', 'chromium', 'edge', 'brave', 'opera', 'vivaldi']

    # Domains that need authentication
    AUTH_DOMAINS = [
        '.codeforces.com',
        '.atcoder.jp',
        # Add more as needed
    ]

    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self._cookie_jar: Optional[http.cookiejar.CookieJar] = None
        self._last_browser: Optional[str] = None

    def extract_cookies(self, domain: Optional[str] = None,
                       force_refresh: bool = False) -> Optional[http.cookiejar.CookieJar]:
        """
        Extract cookies from browser.

        Args:
            domain: Specific domain to extract (e.g., 'codeforces.com')
            force_refresh: Ignore cache and re-extract from browser

        Returns:
            CookieJar with extracted cookies, or None if extraction fails
        """
        if not COOKIE_SUPPORT:
            return None

        # Load config to get preferences
        from .config import load_config
        config = load_config()
        max_age_hours = config.get('cookie_cache_max_age_hours', 24)

        # Try cache first
        if self.cache_enabled and not force_refresh:
            cached = self._load_from_cache()
            if cached and not cached.is_expired(max_age_hours):
                return self._dict_to_cookiejar(cached.cookies)

        # Extract from browser
        from .io import info
        if force_refresh:
            info("  (refreshing cookies...)")
        else:
            info("  (extracting cookies...)")

        cookie_jar = self._extract_from_browser(domain, config)

        # Cache the result
        if cookie_jar and self.cache_enabled:
            self._save_to_cache(cookie_jar)

        return cookie_jar

    def _extract_from_browser(self, domain: Optional[str],
                             config: Dict) -> Optional[http.cookiejar.CookieJar]:
        """Try to extract cookies from available browsers in priority order."""
        # Try user's preferred browser first
        preferred = config.get('preferred_browser')
        if preferred:
            try:
                cookie_jar = self._try_browser(preferred, domain)
                if cookie_jar and len(cookie_jar) > 0:
                    self._last_browser = preferred
                    return cookie_jar
            except Exception:
                pass

        # Try to detect system default browser
        default_browser = self.detect_default_browser()
        if default_browser:
            try:
                cookie_jar = self._try_browser(default_browser, domain)
                if cookie_jar and len(cookie_jar) > 0:
                    self._last_browser = default_browser
                    return cookie_jar
            except Exception:
                pass

        # Try all browsers in priority order
        for browser_name in self.BROWSERS:
            try:
                cookie_jar = self._try_browser(browser_name, domain)
                if cookie_jar and len(cookie_jar) > 0:
                    self._last_browser = browser_name
                    return cookie_jar
            except Exception:
                continue

        return None

    def detect_default_browser(self) -> Optional[str]:
        """
        Detect the system's default browser.

        Returns:
            Browser name (e.g., 'firefox', 'chrome'), or None if detection fails
        """
        try:
            # Linux: use xdg-settings
            if os.name == 'posix' and os.path.exists('/usr/bin/xdg-settings'):
                result = subprocess.run(
                    ['xdg-settings', 'get', 'default-web-browser'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    browser_desktop = result.stdout.strip().lower()
                    # Map desktop file names to browser names
                    if 'firefox' in browser_desktop or 'zen' in browser_desktop:
                        return 'firefox'
                    elif 'chrome' in browser_desktop:
                        return 'chrome'
                    elif 'chromium' in browser_desktop:
                        return 'chromium'
                    elif 'brave' in browser_desktop:
                        return 'brave'
                    elif 'edge' in browser_desktop:
                        return 'edge'
                    elif 'vivaldi' in browser_desktop:
                        return 'vivaldi'
                    elif 'opera' in browser_desktop:
                        return 'opera'

            # macOS: defaults read
            elif os.name == 'darwin':
                # macOS default browser detection would go here
                pass

            # Windows: registry
            elif os.name == 'nt':
                # Windows default browser detection would go here
                pass

        except Exception:
            pass

        return None

    def _try_browser(self, browser_name: str,
                    domain: Optional[str]) -> Optional[http.cookiejar.CookieJar]:
        """Attempt to extract cookies from a specific browser."""
        # Special handling for ZEN browser
        if browser_name == 'zen':
            return self._try_zen_browser(domain)

        browser_funcs = {
            'firefox': browser_cookie3.firefox,
            'chrome': browser_cookie3.chrome,
            'chromium': browser_cookie3.chromium,
            'edge': browser_cookie3.edge,
            'brave': browser_cookie3.brave,
            'opera': browser_cookie3.opera,
            'vivaldi': browser_cookie3.chrome,  # Vivaldi uses Chrome's format
        }

        if browser_name not in browser_funcs:
            return None

        try:
            if domain:
                return browser_funcs[browser_name](domain_name=domain)
            else:
                return browser_funcs[browser_name]()
        except Exception:
            return None

    def _try_zen_browser(self, domain: Optional[str]) -> Optional[http.cookiejar.CookieJar]:
        """Try to extract cookies from ZEN browser."""
        import glob
        import sqlite3
        import shutil
        import tempfile

        # ZEN uses Firefox format but stores in ~/.zen/
        zen_dir = os.path.expanduser('~/.zen')
        if not os.path.exists(zen_dir):
            return None

        # Find cookie database (similar to Firefox structure)
        cookie_files = glob.glob(os.path.join(zen_dir, '*/cookies.sqlite'))
        if not cookie_files:
            return None

        # Use the most recently modified profile
        cookie_file = max(cookie_files, key=os.path.getmtime)

        try:
            # Copy database to temp file (browser might have it locked)
            with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as tmp:
                tmp_path = tmp.name
                shutil.copy2(cookie_file, tmp_path)

            # Read cookies from SQLite database
            jar = http.cookiejar.CookieJar()
            conn = sqlite3.connect(tmp_path)
            cursor = conn.cursor()

            # Firefox cookie table structure
            query = """
                SELECT host, name, value, path, expiry, isSecure
                FROM moz_cookies
            """

            if domain:
                query += " WHERE host LIKE ?"
                cursor.execute(query, (f'%{domain}%',))
            else:
                cursor.execute(query)

            for row in cursor.fetchall():
                host, name, value, path, expiry, is_secure = row

                cookie = http.cookiejar.Cookie(
                    version=0,
                    name=name,
                    value=value,
                    port=None,
                    port_specified=False,
                    domain=host,
                    domain_specified=True,
                    domain_initial_dot=host.startswith('.'),
                    path=path,
                    path_specified=True,
                    secure=bool(is_secure),
                    expires=expiry,
                    discard=False,
                    comment=None,
                    comment_url=None,
                    rest={},
                    rfc2109=False
                )
                jar.set_cookie(cookie)

            conn.close()
            os.unlink(tmp_path)

            return jar if len(jar) > 0 else None

        except Exception as e:
            return None

    def _load_from_cache(self) -> Optional[CookieCache]:
        """Load cached cookies from disk."""
        if not os.path.exists(self.CACHE_FILE):
            return None

        try:
            with open(self.CACHE_FILE, 'r') as f:
                data = json.load(f)
                return CookieCache(**data)
        except Exception:
            return None

    def _save_to_cache(self, cookie_jar: http.cookiejar.CookieJar):
        """Save cookies to cache file."""
        os.makedirs(self.CACHE_DIR, exist_ok=True)

        cache_data = CookieCache(
            cookies=self._cookiejar_to_dict(cookie_jar),
            extracted_at=time.time(),
            browser=self._last_browser or 'unknown'
        )

        try:
            with open(self.CACHE_FILE, 'w') as f:
                json.dump(asdict(cache_data), f, indent=2)
        except Exception:
            pass  # Silently fail on cache write errors

    def _cookiejar_to_dict(self, cookie_jar: http.cookiejar.CookieJar) -> Dict[str, Dict[str, str]]:
        """Convert CookieJar to dictionary for caching."""
        result = {}
        for cookie in cookie_jar:
            domain = cookie.domain
            if domain not in result:
                result[domain] = {}
            result[domain][cookie.name] = cookie.value
        return result

    def _dict_to_cookiejar(self, cookie_dict: Dict[str, Dict[str, str]]) -> http.cookiejar.CookieJar:
        """Convert cached dictionary back to CookieJar."""
        jar = http.cookiejar.CookieJar()
        for domain, cookies in cookie_dict.items():
            for name, value in cookies.items():
                cookie = http.cookiejar.Cookie(
                    version=0, name=name, value=value,
                    port=None, port_specified=False,
                    domain=domain, domain_specified=True, domain_initial_dot=domain.startswith('.'),
                    path='/', path_specified=True,
                    secure=True, expires=None, discard=True,
                    comment=None, comment_url=None,
                    rest={}, rfc2109=False
                )
                jar.set_cookie(cookie)
        return jar

    def get_cookies_for_domain(self, domain: str) -> Dict[str, str]:
        """
        Get cookies as a simple dict for a specific domain.

        Args:
            domain: Domain like 'codeforces.com'

        Returns:
            Dict of cookie name -> value
        """
        cookie_jar = self.extract_cookies(domain)
        if not cookie_jar:
            return {}

        cookies = {}
        for cookie in cookie_jar:
            if domain in cookie.domain or cookie.domain in domain:
                cookies[cookie.name] = cookie.value

        return cookies

    def clear_cache(self):
        """Clear the cookie cache."""
        if os.path.exists(self.CACHE_FILE):
            os.remove(self.CACHE_FILE)


# Global extractor instance
_extractor: Optional[CookieExtractor] = None

def get_cookie_extractor() -> CookieExtractor:
    """Get or create the global cookie extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = CookieExtractor()
    return _extractor
