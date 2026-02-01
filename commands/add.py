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

from .common import Colors, get_repo_root
from .config import load_config
from lib import (
    parse_problem_url,
    generate_header,
    create_problem_file,
    detect_judge
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "template.cpp")


def add_from_url(url):
    """Create a problem file from a URL."""
    config = load_config()
    info = parse_problem_url(url)

    if not info:
        print(f"{Colors.FAIL}Error: could not parse URL.{Colors.ENDC}")
        print(f"  Supported: codeforces.com, atcoder.jp, cses.fi, judge.yosupo.jp")
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
        print(f"{Colors.WARNING}{filename} already exists in {dest_dir}.{Colors.ENDC}")
        return

    # Try to fetch problem name using judges
    problem_name = None
    judge = detect_judge(url)
    if judge:
        try:
            problem_name = judge.fetch_problem_name(info['contest_id'], info['letter'])
        except Exception:
            pass

    # Generate header and create file
    header = generate_header(
        problem_id=info['letter'],
        link=info['link'],
        problem_name=problem_name,
        author=config["author"]
    )
    create_problem_file(filepath, TEMPLATE_PATH, header)

    print(f"{Colors.GREEN}+ {filename} created in {dest_dir}{Colors.ENDC}")

    # Try to fetch samples
    if judge:
        try:
            from .fetch import fetch_problem
            fetch_problem(info['filename'], dest_dir)
        except Exception:
            pass

    # Update info.md
    try:
        from .update import generate_info_md
        generate_info_md(dest_dir)
    except Exception:
        pass


def add_from_name(name, directory):
    """Create a problem file from a name in the given directory."""
    config = load_config()

    if not os.path.exists(TEMPLATE_PATH):
        print(f"{Colors.FAIL}Error: template.cpp not found.{Colors.ENDC}")
        sys.exit(1)

    filename = f"{name}.cpp"
    filepath = os.path.join(directory, filename)

    if os.path.exists(filepath):
        print(f"{Colors.WARNING}{filename} already exists.{Colors.ENDC}")
        return

    # Check if sibling files exist to inherit link
    link = ""
    problem_name = None

    # Try to find a sibling file (e.g., if adding A-brute, look for A.cpp)
    base_name = name.split('-')[0]  # A-brute -> A
    sibling_path = os.path.join(directory, f"{base_name}.cpp")

    if os.path.exists(sibling_path):
        try:
            from .update import read_problem_info
            sibling_info = read_problem_info(sibling_path)
            if sibling_info and sibling_info.get('link'):
                link = sibling_info['link']
                if sibling_info.get('problem'):
                    # Extract just the problem name part (after the letter)
                    parts = sibling_info['problem'].split(' - ', 1)
                    if len(parts) > 1:
                        problem_name = parts[1]
        except Exception:
            pass

    header = generate_header(
        problem_id=name,
        link=link,
        problem_name=problem_name,
        author=config["author"]
    )
    create_problem_file(filepath, TEMPLATE_PATH, header)

    print(f"{Colors.GREEN}+ {filename} created{Colors.ENDC}")


def main():
    if len(sys.argv) < 2:
        print(f"{Colors.FAIL}Usage: cptools add <name> [directory]{Colors.ENDC}")
        print(f"       cptools add <url>")
        print(f"  Examples:")
        print(f"    cptools add A")
        print(f"    cptools add https://codeforces.com/contest/1234/problem/A")
        sys.exit(1)

    arg = sys.argv[1]

    # Detect if arg is a URL
    if arg.startswith('http://') or arg.startswith('https://'):
        add_from_url(arg)
    else:
        # Get directory from second arg if provided
        directory = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
        add_from_name(arg, directory)


if __name__ == "__main__":
    main()
