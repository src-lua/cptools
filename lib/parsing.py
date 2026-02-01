"""
Parsing utilities for problem ranges, problem URLs, and contest URLs.

This module centralizes all parsing logic to eliminate duplication across commands.
"""
import re


def parse_problem_range(input_str):
    """
    Parse problem range (A~E) or list (A B C).

    Args:
        input_str: Input like "A~E", "A B C", "A,B,C", or single "A"

    Returns:
        List of problem identifiers

    Examples:
        >>> parse_problem_range("A~E")
        ['A', 'B', 'C', 'D', 'E']
        >>> parse_problem_range("A B C")
        ['A', 'B', 'C']
        >>> parse_problem_range("A,B,C")
        ['A', 'B', 'C']
        >>> parse_problem_range("A")
        ['A']
    """
    if '~' in input_str:
        parts = input_str.split('~')
        if len(parts) == 2 and len(parts[0].strip()) == 1 and len(parts[1].strip()) == 1:
            # Only uppercase for single-letter ranges
            start = ord(parts[0].strip().upper())
            end = ord(parts[1].strip().upper())
            return [chr(i) for i in range(start, end + 1)]
    # Preserve original case for non-range inputs
    return input_str.replace(',', ' ').split()


def parse_problem_url(url):
    """
    Parse a single problem URL into platform info.

    Args:
        url: Problem URL from Codeforces, AtCoder, Yosupo, CSES, etc.

    Returns:
        Dictionary with platform info:
        {
            'platform_dir': str,     # Directory path like 'Codeforces/Problemset'
            'contest_id': str,       # Contest/problem set ID
            'letter': str,           # Problem letter/ID
            'filename': str,         # Suggested filename (without .cpp)
            'link': str,             # Original URL
            'fetch_platform': str,   # Platform identifier for fetching
        }
        Or None if URL not recognized

    Examples:
        >>> parse_problem_url("https://codeforces.com/contest/1234/problem/A")
        {'platform_dir': 'Codeforces/Problemset', 'contest_id': '1234', ...}
    """
    url = url.strip()

    # CF problemset: codeforces.com/problemset/problem/1234/A
    match = re.search(r'codeforces\.com/problemset/problem/(\d+)/([A-Za-z]\d*)', url)
    if match:
        return {
            'platform_dir': 'Codeforces/Problemset',
            'contest_id': match.group(1),
            'letter': match.group(2),
            'filename': f"{match.group(1)}{match.group(2)}",
            'link': url,
            'fetch_platform': 'codeforces',
        }

    # CF contest: codeforces.com/contest/1234/problem/A
    match = re.search(r'codeforces\.com/contest/(\d+)/problem/([A-Za-z]\d*)', url)
    if match:
        return {
            'platform_dir': 'Codeforces/Problemset',
            'contest_id': match.group(1),
            'letter': match.group(2),
            'filename': f"{match.group(1)}{match.group(2)}",
            'link': url,
            'fetch_platform': 'codeforces',
        }

    # CF gym: codeforces.com/gym/12345/problem/A
    match = re.search(r'codeforces\.com/gym/(\d+)/problem/([A-Za-z]\d*)', url)
    if match:
        return {
            'platform_dir': 'Codeforces/Problemset',
            'contest_id': match.group(1),
            'letter': match.group(2),
            'filename': f"gym{match.group(1)}{match.group(2)}",
            'link': url,
            'fetch_platform': 'codeforces',
        }

    # AtCoder: atcoder.jp/contests/abc300/tasks/abc300_a
    match = re.search(r'atcoder\.jp/contests/([^/]+)/tasks/([^/?#]+)', url)
    if match:
        task_id = match.group(2)
        return {
            'platform_dir': 'AtCoder/Problemset',
            'contest_id': match.group(1),
            'letter': task_id.split('_')[-1].upper() if '_' in task_id else task_id,
            'filename': task_id,
            'link': url,
            'fetch_platform': 'atcoder',
        }

    # Yosupo Library Checker: judge.yosupo.jp/problem/{name}
    match = re.search(r'judge\.yosupo\.jp/problem/([^/?#]+)', url)
    if match:
        problem_name = match.group(1)
        return {
            'platform_dir': 'Yosupo',
            'contest_id': problem_name,
            'letter': problem_name,
            'filename': problem_name,
            'link': url,
            'fetch_platform': 'yosupo',
        }

    # CSES: cses.fi/problemset/task/1636
    match = re.search(r'cses\.fi/problemset/task/(\d+)', url)
    if match:
        problem_id = match.group(1)
        return {
            'platform_dir': 'CSES',
            'contest_id': 'problemset',
            'letter': problem_id,
            'filename': problem_id,
            'link': url,
            'fetch_platform': 'cses',
        }

    return None


def parse_contest_url(url):
    """
    Parse a contest URL.

    Args:
        url: Contest URL from Codeforces, AtCoder, vJudge, etc.

    Returns:
        Dictionary with contest info:
        {
            'platform': str,          # Platform directory name
            'base_url': str,          # URL template with placeholders
            'is_training': bool,      # Whether it's a training/group contest
            'contest_id': str,        # Contest identifier
            'group_id': str | None,   # Group ID for CF trainings
            'default_range': str | None,  # Detected problem range like "A~D"
        }
        Or None if URL not recognized

    Examples:
        >>> parse_contest_url("https://codeforces.com/contest/1234")
        {'platform': 'Codeforces', 'contest_id': '1234', ...}
    """
    url = url.strip()

    # Extract problem letter from URL if present for default range detection
    problem_match = re.search(r'(?:problem/|tasks/[^/]+_)([A-Za-z])', url)
    default_range = None
    if problem_match:
        problem_char = problem_match.group(1).upper()
        default_range = f"A~{problem_char}"

    # Codeforces group/training: codeforces.com/group/{id}/contest/{id}
    cf_group_pattern = r'codeforces\.com/group/([^/]+)/contest/(\d+)'
    match = re.search(cf_group_pattern, url)
    if match:
        return {
            'platform': 'Trainings',
            'base_url': 'https://codeforces.com/group/{group_id}/contest/{id}/problem/{char}',
            'is_training': True,
            'group_id': match.group(1),
            'contest_id': match.group(2),
            'default_range': default_range
        }

    # Codeforces gym: codeforces.com/gym/12345
    cf_gym_pattern = r'codeforces\.com/gym/(\d+)'
    match = re.search(cf_gym_pattern, url)
    if match:
        return {
            'platform': 'Codeforces/Gym',
            'base_url': 'https://codeforces.com/gym/{id}/problem/{char}',
            'is_training': False,
            'contest_id': match.group(1),
            'default_range': default_range
        }

    # Codeforces regular contest: codeforces.com/contest/1234
    cf_contest_pattern = r'codeforces\.com/contest/(\d+)'
    match = re.search(cf_contest_pattern, url)
    if match:
        return {
            'platform': 'Codeforces',
            'base_url': 'https://codeforces.com/contest/{id}/problem/{char}',
            'is_training': False,
            'contest_id': match.group(1),
            'default_range': default_range
        }

    # vJudge: vjudge.net/contest/12345
    vjudge_pattern = r'vjudge\.net/contest/(\d+)'
    match = re.search(vjudge_pattern, url)
    if match:
        return {
            'platform': 'vJudge',
            'base_url': 'https://vjudge.net/contest/{id}#problem/{char}',
            'is_training': False,
            'contest_id': match.group(1),
            'default_range': default_range
        }

    # AtCoder: atcoder.jp/contests/abc300
    atcoder_pattern = r'atcoder\.jp/contests/([^/]+)'
    match = re.search(atcoder_pattern, url)
    if match:
        return {
            'platform': 'AtCoder',
            'base_url': 'https://atcoder.jp/contests/{id}/tasks/{id}_{char}',
            'is_training': False,
            'contest_id': match.group(1),
            'default_range': default_range
        }

    return None
