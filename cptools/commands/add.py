#!/usr/bin/env python3
"""
Usage: cptools add <name_or_url> [directory] [options]

Create a new .cpp file with the standard header and template.

Options:
  -f, --fetch   Fetch test cases (only when adding via URL)

Examples:
  cptools add A
  cptools add https://codeforces.com/contest/1234/problem/A
  cptools add https://codeforces.com/contest/1234/problem/A -f
"""
import os
import re
import sys
import argparse

from cptools.lib.fileops import get_repo_root
from cptools.lib.config import load_config
from cptools.lib import (
    parse_problem_url,
    generate_header,
    create_problem_file,
    detect_judge
)
from cptools.lib.io import error, success, warning, log, Colors

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "lib", "templates", "template.cpp")


def _next_version(directory, name):
    """Return next available version index i such that NAME_i.cpp doesn't exist."""
    i = 2
    while os.path.exists(os.path.join(directory, f"{name}_{i}.cpp")):
        i += 1
    return i


def _prompt_version(filename, versioned_name):
    """Ask user whether to create a versioned file. Returns True if confirmed."""
    try:
        answer = input(
            f"{Colors.WARNING}{filename} already exists. "
            f"Create {versioned_name}.cpp? [y/N]{Colors.ENDC} "
        ).strip().lower()
        return answer == 'y'
    except (KeyboardInterrupt, EOFError):
        print()
        return False


def add_from_url(url, autofetch):
    """Create a problem file from a URL."""
    config = load_config()
    info = parse_problem_url(url)

    if not info:
        error("Error: could not parse URL.")
        log("  Supported: codeforces.com, atcoder.jp, cses.fi, judge.yosupo.jp, spoj.com")
        sys.exit(1)

    if not os.path.exists(TEMPLATE_PATH):
        error("Error: template.cpp not found.")
        sys.exit(1)

    root_dir = get_repo_root()
    dest_dir = os.path.join(root_dir, info['platform_dir'])
    os.makedirs(dest_dir, exist_ok=True)

    filename = f"{info['filename']}.cpp"
    filepath = os.path.join(dest_dir, filename)

    if os.path.exists(filepath):
        next_ver = _next_version(dest_dir, info['filename'])
        versioned_name = f"{info['filename']}_{next_ver}"
        if not _prompt_version(filename, versioned_name):
            warning(f"{filename} already exists in {dest_dir}.")
            return
        filename = f"{versioned_name}.cpp"
        filepath = os.path.join(dest_dir, filename)
        # problem_id stays info['letter'] — same problem, different attempt

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

    success(f"+ {filename} created in {dest_dir}")

    # Try to fetch samples
    if judge and autofetch:
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
        error("Error: template.cpp not found.")
        sys.exit(1)

    filename = f"{name}.cpp"
    filepath = os.path.join(directory, filename)
    original_path = None
    original_name = name

    if os.path.exists(filepath):
        next_ver = _next_version(directory, name)
        versioned_name = f"{name}_{next_ver}"
        if not _prompt_version(filename, versioned_name):
            warning(f"{filename} already exists.")
            return
        original_path = filepath
        name = versioned_name
        filename = f"{name}.cpp"
        filepath = os.path.join(directory, filename)

    # Check if sibling files exist to inherit link
    link = ""
    problem_name = None

    # Sibling lookup: original file (versioning) or base name (variant like A-brute)
    if original_path:
        sibling_path = original_path
    else:
        base_name = name.split('-')[0]  # A-brute -> A
        base_name = re.sub(r'_\d+$', '', base_name)  # A_2 -> A (safety net)
        sibling_path = os.path.join(directory, f"{base_name}.cpp")

    if os.path.exists(sibling_path):
        try:
            from cptools.lib.fileops import read_problem_header
            sibling_info = read_problem_header(sibling_path)
            if sibling_info and sibling_info.link:
                link = sibling_info.link
                if sibling_info.problem:
                    parts = sibling_info.problem.split(' - ', 1)
                    if len(parts) > 1:
                        problem_name = parts[1]
        except Exception:
            pass

    header = generate_header(
        problem_id=original_name,  # versioned files use original name (A, not A_2)
        link=link,
        problem_name=problem_name,
        author=config["author"]
    )
    create_problem_file(filepath, TEMPLATE_PATH, header)

    success(f"+ {filename} created")


def get_parser():
    """Creates and returns the argparse parser for the add command."""
    parser = argparse.ArgumentParser(description="Create a new .cpp file with the standard header and template.")
    parser.add_argument('name_or_url', help='Problem name or URL')
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Target directory (for name-based add)')
    parser.add_argument('-f', '--fetch', action='store_true', help='Fetch test cases (only when adding via URL)')
    return parser


def run():
    parser = get_parser()
    args = parser.parse_args()

    arg = args.name_or_url

    # Detect if arg is a URL
    if arg.startswith('http://') or arg.startswith('https://'):
        add_from_url(arg, args.fetch)
    else:
        add_from_name(arg, args.directory)
