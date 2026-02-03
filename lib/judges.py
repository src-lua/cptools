"""
Online judge platform abstractions.

This module provides a unified interface for interacting with different
competitive programming platforms (Codeforces, AtCoder, CSES, etc.).
"""
import re
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict

from .http_utils import fetch_url, fetch_json


@dataclass
class ProblemInfo:
    """Metadata about a problem."""
    index: str
    name: str
    link: str


@dataclass
class SampleTest:
    """A sample test case."""
    input: str
    output: str


def clean_sample_text(text):
    """
    Clean HTML from sample text.

    Args:
        text: Raw HTML text

    Returns:
        Cleaned text with HTML removed and entities decoded
    """
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</div>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = re.sub(r'\n{2,}', '\n', text)
    text = text.strip()
    return text


class Judge(ABC):
    """Base class for online judge platforms."""

    platform_name: str = "Unknown"

    @abstractmethod
    def detect(self, url: str) -> bool:
        """
        Check if URL belongs to this judge.

        Args:
            url: Problem or contest URL

        Returns:
            True if URL matches this platform
        """
        pass

    @abstractmethod
    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        """
        Fetch a single problem's name.

        Args:
            contest_id: Contest/problemset identifier
            problem_id: Problem letter/ID

        Returns:
            Problem name, or None if fetch fails
        """
        pass

    @abstractmethod
    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        """
        Fetch all problems in a contest.

        Args:
            contest_id: Contest identifier

        Returns:
            Dict mapping problem index to name: {"A": "Problem A Name", ...}
        """
        pass

    @abstractmethod
    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        """
        Fetch sample test cases from a problem URL.

        Args:
            url: Problem URL

        Returns:
            List of SampleTest objects, or None if fetch fails
        """
        pass


class CodeforcesJudge(Judge):
    """Codeforces platform (including Gym)."""
    platform_name = "Codeforces"

    def detect(self, url: str) -> bool:
        return 'codeforces.com' in url

    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        """Fetch problem name using Codeforces API."""
        try:
            api_url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=1"
            data = fetch_json(api_url, timeout=10)

            if data['status'] == 'OK':
                for p in data['result']['problems']:
                    if p['index'] == problem_id:
                        return p['name']
        except Exception:
            pass
        return None

    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        """Fetch all problems using Codeforces API."""
        try:
            api_url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=1"
            data = fetch_json(api_url, timeout=10)

            if data['status'] == 'OK':
                return {p['index']: p['name'] for p in data['result']['problems']}
        except Exception:
            pass
        return {}

    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        """Fetch samples by parsing HTML."""
        try:
            html = fetch_url(url, timeout=15)
            return self._parse_samples(html)
        except Exception:
            return None

    def _parse_samples(self, html: str) -> List[SampleTest]:
        """Parse sample tests from Codeforces HTML."""
        samples = []

        # Find sample test section
        start = html.find('<div class="sample-test">')
        if start == -1:
            return samples

        section = html[start:]

        inputs = re.findall(r'<div class="input">.*?<pre[^>]*>(.*?)</pre>', section, re.DOTALL)
        outputs = re.findall(r'<div class="output">.*?<pre[^>]*>(.*?)</pre>', section, re.DOTALL)

        for inp, out in zip(inputs, outputs):
            samples.append(SampleTest(
                input=clean_sample_text(inp),
                output=clean_sample_text(out)
            ))

        return samples


class AtCoderJudge(Judge):
    """AtCoder platform."""
    platform_name = "AtCoder"

    def detect(self, url: str) -> bool:
        return 'atcoder.jp' in url

    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        """Fetch problem name by parsing contest tasks page."""
        try:
            url = f"https://atcoder.jp/contests/{contest_id}/tasks"
            html = fetch_url(url, timeout=10)

            # Look for task in HTML table
            pattern = r'<tr>.*?/tasks/' + re.escape(problem_id) + r'"[^>]*>[^<]*</a>.*?<td[^>]*><a[^>]*>([^<]+)</a></td>'
            match = re.search(pattern, html, re.DOTALL)
            if match:
                return match.group(1).strip()
        except Exception:
            pass
        return None

    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        """Fetch all problems by parsing tasks page."""
        try:
            url = f"https://atcoder.jp/contests/{contest_id}/tasks"
            html = fetch_url(url, timeout=10)

            problems = {}
            # Parse table rows for tasks
            # This is simplified - full implementation would parse the entire table
            pattern = r'<tr>.*?/tasks/([^"]+)"[^>]*>([^<]+)</a>.*?<td[^>]*><a[^>]*>([^<]+)</a></td>'
            matches = re.findall(pattern, html, re.DOTALL)

            for task_id, _, name in matches:
                # Extract letter from task_id (e.g., "abc300_a" -> "A")
                letter = task_id.split('_')[-1].upper() if '_' in task_id else task_id
                problems[letter] = name.strip()

            return problems
        except Exception:
            pass
        return {}

    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        """Fetch samples by parsing HTML."""
        try:
            html = fetch_url(url, timeout=15)
            return self._parse_samples(html)
        except Exception:
            return None

    def _parse_samples(self, html: str) -> List[SampleTest]:
        """Parse sample tests from AtCoder HTML."""
        samples = []

        # AtCoder uses <h3>Sample Input 1</h3> followed by <pre>...</pre>
        # Match both English and Japanese headers
        input_pattern = r'(?:Sample Input|入力例)\s*(\d+)\s*</h3>\s*<pre>(.*?)</pre>'
        output_pattern = r'(?:Sample Output|出力例)\s*(\d+)\s*</h3>\s*<pre>(.*?)</pre>'

        inputs = re.findall(input_pattern, html, re.DOTALL)
        outputs = re.findall(output_pattern, html, re.DOTALL)

        input_map = {num: text for num, text in inputs}
        output_map = {num: text for num, text in outputs}

        for num in sorted(input_map.keys()):
            samples.append(SampleTest(
                input=clean_sample_text(input_map[num]),
                output=clean_sample_text(output_map.get(num, ''))
            ))

        return samples


class CSESJudge(Judge):
    """CSES Problem Set."""
    platform_name = "CSES"

    def detect(self, url: str) -> bool:
        return 'cses.fi' in url

    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        """Fetch problem name by parsing problem page."""
        try:
            url = f"https://cses.fi/problemset/task/{problem_id}"
            html = fetch_url(url, timeout=10)

            # Extract title from <title>CSES - Problem Title</title>
            match = re.search(r'<title>CSES - ([^<]+)</title>', html)
            if match:
                return match.group(1).strip()
        except Exception:
            pass
        return None

    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        """CSES doesn't have contests, return empty dict."""
        return {}

    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        """Fetch samples by parsing HTML."""
        try:
            html = fetch_url(url, timeout=15)
            return self._parse_samples(html)
        except Exception:
            return None

    def _parse_samples(self, html: str) -> List[SampleTest]:
        """Parse sample tests from CSES HTML."""
        samples = []

        # CSES uses <p>Input:</p> followed by <pre>...</pre>
        input_pattern = r'<p>Input:</p>\s*<pre>(.*?)</pre>'
        output_pattern = r'<p>Output:</p>\s*<pre>(.*?)</pre>'

        inputs = re.findall(input_pattern, html, re.DOTALL)
        outputs = re.findall(output_pattern, html, re.DOTALL)

        for inp, out in zip(inputs, outputs):
            samples.append(SampleTest(
                input=clean_sample_text(inp),
                output=clean_sample_text(out)
            ))

        return samples


class YosupoJudge(Judge):
    """Yosupo Library Checker."""
    platform_name = "Yosupo"

    def detect(self, url: str) -> bool:
        return 'judge.yosupo.jp' in url

    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        """Problem names are URL slugs, just title-case them."""
        return problem_id.replace('_', ' ').title()

    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        """Yosupo doesn't have traditional contests."""
        return {}

    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        """Sample fetching not supported for Yosupo."""
        return None


class VJudgeJudge(Judge):
    """vJudge platform (aggregates problems from other judges)."""
    platform_name = "vJudge"

    def detect(self, url: str) -> bool:
        return 'vjudge.net' in url

    def fetch_problem_name(self, contest_id: str, problem_id: str) -> Optional[str]:
        """vJudge fetching not implemented yet."""
        return None

    def fetch_contest_problems(self, contest_id: str) -> Dict[str, str]:
        """vJudge fetching not implemented yet."""
        return {}

    def fetch_samples(self, url: str) -> Optional[List[SampleTest]]:
        """vJudge sample fetching not implemented yet."""
        return None


# Registry of all available judges
ALL_JUDGES: List[Judge] = [
    CodeforcesJudge(),
    AtCoderJudge(),
    CSESJudge(),
    YosupoJudge(),
    VJudgeJudge(),
]


def detect_judge(url: str) -> Optional[Judge]:
    """
    Detect which judge a URL belongs to.

    Args:
        url: Problem or contest URL

    Returns:
        Judge instance if detected, None otherwise

    Examples:
        >>> judge = detect_judge("https://codeforces.com/contest/1234/problem/A")
        >>> type(judge).__name__
        'CodeforcesJudge'
    """
    for judge in ALL_JUDGES:
        if judge.detect(url):
            return judge
    return None
