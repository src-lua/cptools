"""
Tests for lib/parsing.py - Problem range/URL parsing utilities.
"""
from lib.parsing import parse_problem_range, parse_problem_url, parse_contest_url


class TestParseProblemRange:
    """Tests for parse_problem_range function."""

    def test_single_problem(self):
        """Test parsing single problem."""
        assert parse_problem_range("A") == ["A"]
        assert parse_problem_range("B") == ["B"]
        assert parse_problem_range("Z") == ["Z"]

    def test_space_separated_list(self):
        """Test parsing space-separated problem list."""
        assert parse_problem_range("A B C") == ["A", "B", "C"]
        assert parse_problem_range("D E F G") == ["D", "E", "F", "G"]

    def test_comma_separated_list(self):
        """Test parsing comma-separated problem list."""
        assert parse_problem_range("A,B,C") == ["A", "B", "C"]
        assert parse_problem_range("A, B, C") == ["A", "B", "C"]

    def test_range_with_tilde(self):
        """Test parsing problem range with tilde."""
        assert parse_problem_range("A~E") == ["A", "B", "C", "D", "E"]
        assert parse_problem_range("B~D") == ["B", "C", "D"]
        assert parse_problem_range("A~C") == ["A", "B", "C"]

    def test_mixed_separators(self):
        """Test parsing with mixed separators."""
        # Space and comma
        assert parse_problem_range("A B, C") == ["A", "B", "C"]

    def test_lowercase_input(self):
        """Test that lowercase letters are converted to uppercase."""
        assert parse_problem_range("a") == ["A"]
        assert parse_problem_range("a~c") == ["A", "B", "C"]

    def test_empty_string(self):
        """Test parsing empty string."""
        assert parse_problem_range("") == []

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled."""
        assert parse_problem_range("  A  B  C  ") == ["A", "B", "C"]


class TestParseProblemUrl:
    """Tests for parse_problem_url function."""

    def test_codeforces_contest_url(self):
        """Test parsing Codeforces contest problem URL."""
        url = "https://codeforces.com/contest/1234/problem/A"
        result = parse_problem_url(url)
        assert result is not None
        assert result['fetch_platform'] == 'codeforces'
        assert result['contest_id'] == '1234'
        assert result['letter'] == 'A'

    def test_codeforces_gym_url(self):
        """Test parsing Codeforces Gym problem URL."""
        url = "https://codeforces.com/gym/102394/problem/B"
        result = parse_problem_url(url)
        assert result is not None
        assert result['fetch_platform'] == 'codeforces'
        assert result['contest_id'] == '102394'
        assert result['letter'] == 'B'

    def test_codeforces_group_url(self):
        """Test parsing Codeforces group problem URL."""
        url = "https://codeforces.com/group/groupId/contest/1234/problem/C"
        result = parse_problem_url(url)
        # Group URLs are not currently supported in parse_problem_url regex
        assert result is None

    def test_atcoder_url(self):
        """Test parsing AtCoder problem URL."""
        url = "https://atcoder.jp/contests/abc123/tasks/abc123_a"
        result = parse_problem_url(url)
        assert result is not None
        assert result['fetch_platform'] == 'atcoder'
        assert result['contest_id'] == 'abc123'
        assert result['letter'] == 'A'

    def test_cses_url(self):
        """Test parsing CSES problem URL."""
        url = "https://cses.fi/problemset/task/1068"
        result = parse_problem_url(url)
        assert result is not None
        assert result['fetch_platform'] == 'cses'
        assert result['letter'] == '1068'

    def test_yosupo_url(self):
        """Test parsing Yosupo Library Checker URL."""
        url = "https://judge.yosupo.jp/problem/aplusb"
        result = parse_problem_url(url)
        assert result is not None
        assert result['fetch_platform'] == 'yosupo'
        assert result['letter'] == 'aplusb'

    def test_vjudge_url(self):
        """Test parsing vJudge problem URL."""
        url = "https://vjudge.net/contest/123456#problem/A"
        result = parse_problem_url(url)
        # vJudge problem URL parsing is not implemented in parse_problem_url
        assert result is None

    def test_invalid_url(self):
        """Test parsing invalid URL returns None."""
        assert parse_problem_url("https://google.com") is None
        assert parse_problem_url("not a url") is None
        assert parse_problem_url("") is None

    def test_http_vs_https(self):
        """Test that both http and https are accepted."""
        url_https = "https://codeforces.com/contest/1234/problem/A"
        url_http = "http://codeforces.com/contest/1234/problem/A"

        result_https = parse_problem_url(url_https)
        result_http = parse_problem_url(url_http)

        assert result_https is not None
        assert result_http is not None
        assert result_https['contest_id'] == result_http['contest_id']


class TestParseContestUrl:
    """Tests for parse_contest_url function."""

    def test_codeforces_contest(self):
        """Test parsing Codeforces contest URL."""
        url = "https://codeforces.com/contest/1234"
        result = parse_contest_url(url)
        assert result is not None
        assert result['platform'] == 'Codeforces'
        assert result['contest_id'] == '1234'

    def test_codeforces_gym(self):
        """Test parsing Codeforces Gym contest URL."""
        url = "https://codeforces.com/gym/102394"
        result = parse_contest_url(url)
        assert result is not None
        assert result['platform'] == 'Codeforces/Gym'
        assert result['contest_id'] == '102394'

    def test_codeforces_group(self):
        """Test parsing Codeforces group contest URL."""
        url = "https://codeforces.com/group/groupId/contest/1234"
        result = parse_contest_url(url)
        assert result is not None
        assert result['platform'] == 'Trainings'
        assert result['group_id'] == 'groupId'
        assert result['contest_id'] == '1234'

    def test_atcoder_contest(self):
        """Test parsing AtCoder contest URL."""
        url = "https://atcoder.jp/contests/abc123"
        result = parse_contest_url(url)
        assert result is not None
        assert result['platform'] == 'AtCoder'
        assert result['contest_id'] == 'abc123'

    def test_vjudge_contest(self):
        """Test parsing vJudge contest URL."""
        url = "https://vjudge.net/contest/123456"
        result = parse_contest_url(url)
        assert result is not None
        assert result['platform'] == 'vJudge'
        assert result['contest_id'] == '123456'

    def test_cses(self):
        """Test parsing CSES problemset URL."""
        url = "https://cses.fi/problemset/"
        result = parse_contest_url(url)
        assert result is not None
        assert result['platform'] == 'CSES'

    def test_yosupo(self):
        """Test parsing Yosupo Library Checker URL."""
        url = "https://judge.yosupo.jp"
        result = parse_contest_url(url)
        assert result is not None
        assert result['platform'] == 'Yosupo'

    def test_invalid_url(self):
        """Test parsing invalid URL returns None."""
        assert parse_contest_url("https://google.com") is None
        assert parse_contest_url("not a url") is None
        assert parse_contest_url("") is None
