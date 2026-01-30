#!/usr/bin/env python3
"""
Create a new .cpp file with the standard header and template.

Usage:
    cptools add <name> [directory]       Add a file in current/given directory
    cptools add <url>                    Add a problem from its URL

Examples:
    cptools add A2                                              # creates A2.cpp in current dir
    cptools add B-brute                                         # creates B-brute.cpp
    cptools add https://codeforces.com/problemset/problem/1/A   # creates in Codeforces/Problemset/
"""
import os
import sys
import re
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

from .common import Colors, get_repo_root
from .config import load_config

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "template.cpp")

_config = load_config()
AUTHOR_NAME = _config["author"]

def generate_header(name, link="", problem_name=None):
    problem_title = f"{name} - {problem_name}" if problem_name else name
    return f"""/**
 * Author:      {AUTHOR_NAME}
 * Problem:     {problem_title}
 * Link:        {link}
 * Status:      ~
 * Created:     {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
 **/

"""

def parse_problem_url(url):
    """Parse a single problem URL into platform info."""
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

    return None

def fetch_problem_name(info):
    """Try to fetch the problem name from the online judge."""
    try:
        if info['fetch_platform'] == 'codeforces':
            api_url = f"https://codeforces.com/api/contest.standings?contestId={info['contest_id']}&from=1&count=1"
            req = Request(api_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            if data['status'] == 'OK':
                for p in data['result']['problems']:
                    if p['index'] == info['letter']:
                        return p['name']
        elif info['fetch_platform'] == 'atcoder':
            url = f"https://atcoder.jp/contests/{info['contest_id']}/tasks"
            req = Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
            pattern = r'<tr>.*?/tasks/' + re.escape(info['filename']) + r'"[^>]*>[^<]*</a>.*?<td[^>]*><a[^>]*>([^<]+)</a></td>'
            match = re.search(pattern, html, re.DOTALL)
            if match:
                return match.group(1).strip()
        elif info['fetch_platform'] == 'yosupo':
            # Yosupo problem names are the URL slug (e.g., "unionfind")
            return info['filename'].replace('_', ' ').title()
    except Exception:
        pass
    return None

def add_from_url(url):
    """Create a problem file from a URL, fetch samples."""
    info = parse_problem_url(url)
    if not info:
        print(f"{Colors.FAIL}Error: could not parse URL.{Colors.ENDC}")
        print(f"  Supported: codeforces.com, atcoder.jp")
        sys.exit(1)

    if not os.path.exists(TEMPLATE_PATH):
        print(f"{Colors.FAIL}Error: template.cpp not found.{Colors.ENDC}")
        sys.exit(1)

    root_dir = get_repo_root()
    dest_dir = os.path.join(root_dir, info['platform_dir'])
    os.makedirs(dest_dir, exist_ok=True)

    filename = f"{info['filename']}.cpp"
    filepath = os.path.join(dest_dir, filename)

    if os.path.exists(filepath):
        print(f"{Colors.WARNING}{filename} already exists.{Colors.ENDC}")
        sys.exit(1)

    # Fetch problem name
    print(f"{Colors.BLUE}Fetching problem info...{Colors.ENDC}")
    problem_name = fetch_problem_name(info)

    with open(TEMPLATE_PATH, 'r') as f:
        template_body = f.read()

    header = generate_header(info['letter'], info['link'], problem_name)

    with open(filepath, 'w') as f:
        f.write(header + template_body)

    display_name = f"{info['letter']} - {problem_name}" if problem_name else info['filename']
    print(f"{Colors.GREEN}+ Created {filename}{Colors.ENDC}")
    print(f"  {Colors.BLUE}{display_name}{Colors.ENDC}")
    print(f"\n{Colors.BOLD}cd \"{dest_dir}\"{Colors.ENDC}")
    print(f"Run {Colors.BLUE}cptools fetch {info['filename']}{Colors.ENDC} to get sample tests.")

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.FAIL}Usage: cptools add <name|url> [directory]{Colors.ENDC}")
        print(f"  Examples: cptools add A2, cptools add https://codeforces.com/...")
        sys.exit(1)

    arg = sys.argv[1]

    # URL mode
    if '://' in arg:
        add_from_url(arg)
        return

    # Normal mode: add file by name
    name = arg
    directory = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()

    if not os.path.isdir(directory):
        print(f"{Colors.FAIL}Error: {directory} is not a valid directory.{Colors.ENDC}")
        sys.exit(1)

    if not os.path.exists(TEMPLATE_PATH):
        print(f"{Colors.FAIL}Error: template.cpp not found.{Colors.ENDC}")
        sys.exit(1)

    filename = name if name.endswith('.cpp') else f"{name}.cpp"
    filepath = os.path.join(directory, filename)

    if os.path.exists(filepath):
        print(f"{Colors.WARNING}{filename} already exists.{Colors.ENDC}")
        sys.exit(1)

    with open(TEMPLATE_PATH, 'r') as f:
        template_body = f.read()

    # Try to inherit link from sibling files (same contest)
    link = ""
    base_letter = name[0].upper()
    sibling = os.path.join(directory, f"{base_letter}.cpp")
    if os.path.exists(sibling):
        with open(sibling, 'r') as f:
            for line in f.read(500).split('\n'):
                if 'Link:' in line:
                    link = line.split('Link:')[1].strip().replace('*/', '').strip()
                    break

    header = generate_header(name, link)

    with open(filepath, 'w') as f:
        f.write(header + template_body)

    print(f"{Colors.GREEN}+ Created {filename}{Colors.ENDC}")
    if link:
        print(f"{Colors.BLUE}  Inherited link from {base_letter}.cpp{Colors.ENDC}")

    from .update_info import generate_info_md
    generate_info_md(directory)

if __name__ == "__main__":
    main()
