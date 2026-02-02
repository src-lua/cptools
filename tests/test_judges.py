"""
Tests for lib/judges.py - Online judge platform abstractions.
"""
from unittest.mock import patch, MagicMock
from lib.judges import (
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
        with patch('lib.judges.fetch_json', return_value=mock_response):
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
        with patch('lib.judges.fetch_url', return_value=html):
            samples = self.judge.fetch_samples("url")
            assert samples is not None
            assert len(samples) == 2
            assert samples[0].input == "1 2"
            assert samples[0].output == "3"
            assert samples[1].input == "4 5"
            assert samples[1].output == "9"


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
        with patch('lib.judges.fetch_url', return_value=html):
            assert self.judge.fetch_problem_name("abc123", "abc123_a") == "Task Name"

    def test_fetch_samples(self):
        html = """
        <h3>Sample Input 1</h3><pre>1 2</pre>
        <h3>Sample Output 1</h3><pre>3</pre>
        <h3>Sample Input 2</h3><pre>4 5</pre>
        <h3>Sample Output 2</h3><pre>9</pre>
        """
        with patch('lib.judges.fetch_url', return_value=html):
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
        with patch('lib.judges.fetch_url', return_value=html):
            assert self.judge.fetch_problem_name("problemset", "1068") == "Weird Algorithm"

    def test_fetch_samples(self):
        html = """
        <p>Input:</p><pre>3</pre>
        <p>Output:</p><pre>3 10 5 16 8 4 2 1</pre>
        """
        with patch('lib.judges.fetch_url', return_value=html):
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