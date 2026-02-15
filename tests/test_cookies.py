"""
Tests for lib/cookies.py - Cookie extraction and management.
"""
import os
import json
import tempfile
import time
from unittest.mock import patch, MagicMock
import pytest
import http.cookiejar

from cptools.lib.cookies import CookieExtractor, CookieCache, get_cookie_extractor


class TestCookieCache:
    """Tests for CookieCache dataclass."""

    def test_cache_expiration(self):
        """Test cache expiration logic."""
        cache = CookieCache(
            cookies={'test.com': {'session': 'abc'}},
            extracted_at=time.time() - (25 * 3600),  # 25 hours ago
            browser='firefox'
        )
        assert cache.is_expired(max_age_hours=24)

        cache.extracted_at = time.time()
        assert not cache.is_expired(max_age_hours=24)

    def test_cache_never_expires_with_minus_one(self):
        """Test that cache never expires when max_age_hours is -1."""
        cache = CookieCache(
            cookies={'test.com': {'session': 'abc'}},
            extracted_at=time.time() - (365 * 24 * 3600),  # 1 year ago
            browser='firefox'
        )
        # Even though it's very old, it should not expire with -1
        assert not cache.is_expired(max_age_hours=-1)


class TestCookieExtractor:
    """Tests for CookieExtractor class."""

    def test_extraction_no_support(self):
        """Test graceful handling when browser_cookie3 not available."""
        with patch('cptools.lib.cookies.COOKIE_SUPPORT', False):
            extractor = CookieExtractor()
            result = extractor.extract_cookies()
            assert result is None

    def test_cache_loading(self):
        """Test loading cookies from cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "browser_cookies.json")
            cache_data = {
                'cookies': {'.codeforces.com': {'JSESSIONID': 'test123'}},
                'extracted_at': time.time(),
                'browser': 'firefox'
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)

            with patch.object(CookieExtractor, 'CACHE_FILE', cache_file):
                extractor = CookieExtractor()
                cached = extractor._load_from_cache()
                assert cached is not None
                assert cached.browser == 'firefox'
                assert '.codeforces.com' in cached.cookies

    def test_dict_conversion(self):
        """Test CookieJar to dict and back conversion."""
        extractor = CookieExtractor()

        # Create test cookie jar
        jar = http.cookiejar.CookieJar()
        cookie = http.cookiejar.Cookie(
            version=0, name='test', value='value',
            port=None, port_specified=False,
            domain='.example.com', domain_specified=True, domain_initial_dot=True,
            path='/', path_specified=True,
            secure=True, expires=None, discard=True,
            comment=None, comment_url=None, rest={}, rfc2109=False
        )
        jar.set_cookie(cookie)

        # Convert to dict and back
        cookie_dict = extractor._cookiejar_to_dict(jar)
        assert '.example.com' in cookie_dict
        assert cookie_dict['.example.com']['test'] == 'value'

        new_jar = extractor._dict_to_cookiejar(cookie_dict)
        assert len(new_jar) == 1

        # Check cookie values
        cookies_list = list(new_jar)
        assert cookies_list[0].name == 'test'
        assert cookies_list[0].value == 'value'

    def test_clear_cache(self):
        """Test cache clearing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "browser_cookies.json")

            # Create cache file
            cache_data = {
                'cookies': {'.codeforces.com': {'JSESSIONID': 'test123'}},
                'extracted_at': time.time(),
                'browser': 'firefox'
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)

            assert os.path.exists(cache_file)

            with patch.object(CookieExtractor, 'CACHE_FILE', cache_file):
                extractor = CookieExtractor()
                extractor.clear_cache()

            assert not os.path.exists(cache_file)

    def test_detect_default_browser_linux(self):
        """Test default browser detection on Linux."""
        extractor = CookieExtractor()

        with patch('os.name', 'posix'), \
             patch('os.path.exists', return_value=True), \
             patch('subprocess.run') as mock_run:

            # Simulate xdg-settings output for Firefox
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='firefox.desktop\n'
            )

            browser = extractor.detect_default_browser()
            assert browser == 'firefox'

            # Simulate xdg-settings output for Chrome
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='google-chrome.desktop\n'
            )

            browser = extractor.detect_default_browser()
            assert browser == 'chrome'

    def test_get_cookies_for_domain(self):
        """Test getting cookies for a specific domain."""
        extractor = CookieExtractor()

        # Create mock cookie jar
        jar = http.cookiejar.CookieJar()
        cookie1 = http.cookiejar.Cookie(
            version=0, name='session', value='abc123',
            port=None, port_specified=False,
            domain='.codeforces.com', domain_specified=True, domain_initial_dot=True,
            path='/', path_specified=True,
            secure=True, expires=None, discard=True,
            comment=None, comment_url=None, rest={}, rfc2109=False
        )
        cookie2 = http.cookiejar.Cookie(
            version=0, name='other', value='xyz789',
            port=None, port_specified=False,
            domain='.example.com', domain_specified=True, domain_initial_dot=True,
            path='/', path_specified=True,
            secure=True, expires=None, discard=True,
            comment=None, comment_url=None, rest={}, rfc2109=False
        )
        jar.set_cookie(cookie1)
        jar.set_cookie(cookie2)

        with patch.object(extractor, 'extract_cookies', return_value=jar):
            cookies = extractor.get_cookies_for_domain('codeforces.com')
            assert 'session' in cookies
            assert cookies['session'] == 'abc123'


def test_get_cookie_extractor_singleton():
    """Test singleton pattern."""
    e1 = get_cookie_extractor()
    e2 = get_cookie_extractor()
    assert e1 is e2
