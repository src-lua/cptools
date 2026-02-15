"""
Tests for lib/judges.py - Online judge platform abstractions.
"""
import pytest
from unittest.mock import patch, MagicMock
from cptools.lib import PlatformError
from cptools.lib.judges import (
    detect_judge,
    CodeforcesJudge,
    AtCoderJudge,
    CSESJudge,
    YosupoJudge,
    VJudgeJudge,
    SampleTest
)


class TestDetectJudge:
    """Tests for detect_judge function."""

    def test_detect_codeforces(self):
        assert isinstance(detect_judge("https://codeforces.com/contest/1234"), CodeforcesJudge)
        assert isinstance(detect_judge("http://codeforces.com/gym/100000"), CodeforcesJudge)

    def test_detect_atcoder(self):
        assert isinstance(detect_judge("https://atcoder.jp/contests/abc100"), AtCoderJudge)

    def test_detect_cses(self):
        assert isinstance(detect_judge("https://cses.fi/problemset/task/1068"), CSESJudge)

    def test_detect_yosupo(self):
        assert isinstance(detect_judge("https://judge.yosupo.jp/problem/aplusb"), YosupoJudge)

    def test_detect_vjudge(self):
        assert isinstance(detect_judge("https://vjudge.net/contest/123456"), VJudgeJudge)

    def test_detect_none(self):
        assert detect_judge("https://google.com") is None
        assert detect_judge("invalid") is None


class TestCodeforcesJudge:
    """Tests for CodeforcesJudge class."""

    def setup_method(self):
        self.judge = CodeforcesJudge()

    def test_fetch_problem_name(self):
        mock_response = {
            "status": "OK",
            "result": {
                "problems": [
                    {"contestId": 1234, "index": "A", "name": "Problem A"},
                    {"contestId": 1234, "index": "B", "name": "Problem B"}
                ]
            }
        }
        with patch('cptools.lib.judges.fetch_json', return_value=mock_response):
            assert self.judge.fetch_problem_name("1234", "A") == "Problem A"
            assert self.judge.fetch_problem_name("1234", "C") is None

    def test_fetch_samples(self):
        html = """
        <div class="sample-test">
            <div class="input"><pre>1 2</pre></div>
            <div class="output"><pre>3</pre></div>
            <div class="input"><pre>4 5</pre></div>
            <div class="output"><pre>9</pre></div>
        </div>
        """
        with patch('cptools.lib.judges.fetch_url', return_value=html):
            samples = self.judge.fetch_samples("url")
            assert samples is not None
            assert len(samples) == 2
            assert samples[0].input == "1 2"
            assert samples[0].output == "3"
            assert samples[1].input == "4 5"
            assert samples[1].output == "9"

    def test_needs_authentication_for_groups(self):
        """Test that group URLs are detected as needing auth."""
        # Group URL needs auth
        assert self.judge.needs_authentication("https://codeforces.com/group/abc123/contest/456/problem/A")

        # Regular contest doesn't
        assert not self.judge.needs_authentication("https://codeforces.com/contest/1234/problem/A")

    def test_is_private_url(self):
        """Test private URL detection."""
        assert self.judge._is_private_url("https://codeforces.com/group/test/contest/123/problem/A")
        assert not self.judge._is_private_url("https://codeforces.com/contest/1234/problem/A")

    def test_fetch_samples_with_auth(self):
        """Test sample fetching uses auth for group URLs."""
        group_url = "https://codeforces.com/group/test/contest/123/problem/A"

        html = """
        <div class="sample-test">
            <div class="input"><pre>1 2</pre></div>
            <div class="output"><pre>3</pre></div>
        </div>
        """

        with patch('cptools.lib.http_utils.fetch_url_with_auth', return_value=html) as mock_fetch:
            samples = self.judge.fetch_samples(group_url)

            # Verify auth fetch was used
            mock_fetch.assert_called_once()
            assert samples is not None
            assert len(samples) == 1
            assert samples[0].input == "1 2"
            assert samples[0].output == "3"

    def test_fetch_with_auth_retry(self):
        """Test that auth retry works when session expires."""
        url = "https://codeforces.com/group/test/contest/123/problem/A"

        # First call returns login page (with actual login form), second returns actual content
        login_html = '<html><form class="loginForm">Please login</form></html>'
        actual_html = """
        <div class="sample-test">
            <div class="input"><pre>1 2</pre></div>
            <div class="output"><pre>3</pre></div>
        </div>
        """

        with patch('cptools.lib.http_utils.fetch_url_with_auth', side_effect=[login_html, actual_html]) as mock_fetch:
            html = self.judge._fetch_with_auth_retry(url)

            # Should have called twice (first failed, second succeeded)
            assert mock_fetch.call_count == 2
            assert html == actual_html

            # First call without force_refresh, second with force_refresh
            calls = mock_fetch.call_args_list
            assert calls[0][1]['force_refresh'] == False
            assert calls[1][1]['force_refresh'] == True

    def test_is_logged_out(self):
        """Test _is_logged_out detection method."""
        # HTML with login indicators (not logged in)
        html_logged_out = '<html><a href="/enter?back=/contest">Enter</a> | <a href="/register">Register</a></html>'
        assert self.judge._is_logged_out(html_logged_out) == True

        # HTML without login indicators (logged in)
        html_logged_in = '<html><a href="/logout">Logout</a></html>'
        assert self.judge._is_logged_out(html_logged_in) == False

        # HTML with samples (likely logged in)
        html_with_samples = '<html><div class="sample-test"><pre>test</pre></div></html>'
        assert self.judge._is_logged_out(html_with_samples) == False

    def test_auto_refresh_on_expired_cookies(self):
        """Test that expired cookies are automatically refreshed."""
        url = "https://codeforces.com/group/test/contest/123/problem/A"

        # First fetch returns HTML indicating not logged in (no samples, has Enter link)
        html_not_logged_in = '<html><a href="/enter?back=/contest">Enter</a></html>'

        # Second fetch (after cookie refresh) returns HTML with samples
        html_with_samples = """
        <html>
        <div class="sample-test">
            <div class="input"><pre>1 2</pre></div>
            <div class="output"><pre>3</pre></div>
        </div>
        </html>
        """

        with patch('cptools.lib.http_utils.fetch_url_with_auth') as mock_fetch_auth:
            # First call returns "not logged in", second returns samples
            mock_fetch_auth.side_effect = [html_not_logged_in, html_with_samples]

            samples = self.judge.fetch_samples(url)

            # Should have called fetch twice: once with cache, once with force_refresh
            assert mock_fetch_auth.call_count == 2

            # Second call should have force_refresh=True
            second_call_kwargs = mock_fetch_auth.call_args_list[1][1]
            assert second_call_kwargs['force_refresh'] == True

            # Should have successfully parsed samples
            assert samples is not None
            assert len(samples) == 1
            assert samples[0].input == "1 2"
            assert samples[0].output == "3"

    def test_error_when_truly_not_logged_in(self):
        """Test error message when user is not logged in after cookie refresh."""
        url = "https://codeforces.com/group/test/contest/123/problem/A"

        # Both fetches return "not logged in" (user is truly not logged in)
        html_not_logged_in = '<html><a href="/enter?back=/contest">Enter</a></html>'

        with patch('cptools.lib.http_utils.fetch_url_with_auth') as mock_fetch_auth:
            mock_fetch_auth.return_value = html_not_logged_in

            # Should raise PlatformError
            with pytest.raises(PlatformError) as exc_info:
                self.judge.fetch_samples(url)

            # Check error message
            assert "Authentication required" in str(exc_info.value)
            assert "not logged in" in str(exc_info.value)

            # Should have tried twice (initial + retry with force_refresh)
            assert mock_fetch_auth.call_count == 2


class TestAtCoderJudge:
    """Tests for AtCoderJudge class."""

    def setup_method(self):
        self.judge = AtCoderJudge()

    def test_fetch_problem_name(self):
        html = """
        <tr>
            <td class="text-center"><a href="/contests/abc123/tasks/abc123_a">A</a></td>
            <td><a href="/contests/abc123/tasks/abc123_a">Task Name</a></td>
        </tr>
        """
        with patch('cptools.lib.judges.fetch_url', return_value=html):
            assert self.judge.fetch_problem_name("abc123", "abc123_a") == "Task Name"

    def test_fetch_samples(self):
        html = """
        <h3>Sample Input 1</h3><pre>1 2</pre>
        <h3>Sample Output 1</h3><pre>3</pre>
        <h3>Sample Input 2</h3><pre>4 5</pre>
        <h3>Sample Output 2</h3><pre>9</pre>
        """
        with patch('cptools.lib.judges.fetch_url', return_value=html):
            samples = self.judge.fetch_samples("url")
            assert samples is not None
            assert len(samples) == 2
            assert samples[0].input == "1 2"
            assert samples[0].output == "3"
            assert samples[1].input == "4 5"
            assert samples[1].output == "9"


class TestCSESJudge:
    """Tests for CSESJudge class."""

    def setup_method(self):
        self.judge = CSESJudge()

    def test_fetch_problem_name(self):
        html = "<title>CSES - Weird Algorithm</title>"
        with patch('cptools.lib.judges.fetch_url', return_value=html):
            assert self.judge.fetch_problem_name("problemset", "1068") == "Weird Algorithm"

    def test_fetch_samples(self):
        html = """
        <p>Input:</p><pre>3</pre>
        <p>Output:</p><pre>3 10 5 16 8 4 2 1</pre>
        """
        with patch('cptools.lib.judges.fetch_url', return_value=html):
            samples = self.judge.fetch_samples("url")
            assert samples is not None
            assert len(samples) == 1
            assert samples[0].input == "3"
            assert samples[0].output == "3 10 5 16 8 4 2 1"


class TestYosupoJudge:
    """Tests for YosupoJudge class."""

    def setup_method(self):
        self.judge = YosupoJudge()

    def test_fetch_problem_name(self):
        # Yosupo just formats the ID
        assert self.judge.fetch_problem_name("yosupo", "aplusb") == "Aplusb"
        assert self.judge.fetch_problem_name("yosupo", "many_aplusb") == "Many Aplusb"


class TestVJudgeJudge:
    """Tests for VJudgeJudge class."""

    def setup_method(self):
        self.judge = VJudgeJudge()

    def test_fetch_not_implemented(self):
        assert self.judge.fetch_problem_name("123", "A") is None
        assert self.judge.fetch_samples("url") is None