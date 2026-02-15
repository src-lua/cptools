#!/usr/bin/env python3
"""
Usage: cptools update [directory] [options]

Generate or update info.md status file for the contest directory.

Options:
  -a, --all     Update all contest directories in the repository

Examples:
  cptools update
  cptools update -a
"""
import os
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path

from cptools.lib.fileops import read_problem_header, get_repo_root, PLATFORM_DIRS
from cptools.lib.io import error, success, warning, info, header, bold
from cptools.lib.display_utils import get_status_emoji
from cptools.lib.path_utils import detect_platform_from_path

def is_problemset(platform, directory_path):
    """
    Determine if this is a problemset (permanent collection) vs contest (time-based event).

    Logic:
    - CSES, Yosupo: Always problemsets
    - Any path containing "/Problemset/": Problemset (e.g., Codeforces/Problemset, AtCoder/Problemset)
    - Everything else: Contest

    Args:
        platform: Platform name from detect_platform_from_path
        directory_path: Full directory path

    Returns:
        True if problemset, False if contest
    """
    # Pure problemset platforms
    if platform in ['CSES', 'Yosupo']:
        return True

    # Any platform with "/Problemset/" in path is a problemset
    if '/Problemset/' in directory_path or directory_path.endswith('/Problemset'):
        return True

    # Everything else is a contest
    return False


def generate_info_md(directory):
    """
    Generate or update info.md for the contest directory.

    This function scans for .cpp files, extracts their problem headers,
    and generates a markdown summary with problem status and progress.

    Problem Variations:
        When multiple files represent the same problem (e.g., different
        implementations or compressed versions), only one is included:

        - Files with suffixes (PROBLEM-suffix.cpp) are considered variations
        - Examples: COT.cpp and COT-compressed.cpp, A.cpp and A-v2.cpp
        - The base version (without suffix) is preferred if it exists
        - If no base version exists, the first variation alphabetically is used

        Examples:
            COT.cpp + COT-compressed.cpp → Uses COT.cpp
            A-v1.cpp + A-v2.cpp → Uses A-v1.cpp (alphabetically first)
            B.cpp + B-optimized.cpp + B-alternative.cpp → Uses B.cpp

    Args:
        directory: Path to contest/problemset directory containing .cpp files
    """
    directory = os.path.abspath(directory)

    # Find all .cpp files
    all_cpp_files = sorted([f for f in os.listdir(directory) if f.endswith('.cpp')])

    if not all_cpp_files:
        warning(f"No .cpp files found in {directory}")
        return

    # Filter out problem variations (files with -suffix)
    # Group files by base name (before first '-')
    problem_groups = {}
    for cpp_file in all_cpp_files:
        # Extract base name (e.g., "COT-compressed.cpp" -> "COT")
        base_name = cpp_file.replace('.cpp', '').split('-')[0]

        if base_name not in problem_groups:
            problem_groups[base_name] = []
        problem_groups[base_name].append(cpp_file)

    # For each group, prefer the version without suffix
    cpp_files = []
    for base_name, files in sorted(problem_groups.items()):
        # Check if base version exists (e.g., "COT.cpp")
        base_file = f"{base_name}.cpp"
        if base_file in files:
            cpp_files.append(base_file)
        else:
            # No base version, use first variation alphabetically
            cpp_files.append(sorted(files)[0])

    info(f"Reading {len(cpp_files)} problem files...")

    # Extract problem information
    problems = []
    for cpp_file in cpp_files:
        filepath = os.path.join(directory, cpp_file)
        header = read_problem_header(filepath)

        if header:
            char = cpp_file.replace('.cpp', '')
            problems.append({
                'char': char,
                'file': cpp_file,
                'problem': header.problem,
                'link': header.link,
                'status': header.status,
                'created': header.created
            })

    if not problems:
        error("No valid problem headers found.")
        return

    # Detect platform and contest
    platform, contest_id = detect_platform_from_path(directory)
    is_pset = is_problemset(platform, directory)

    # Generate markdown content
    content = f"# {platform}"
    if contest_id != Path(directory).name:
        content += f" - {contest_id}"
    content += "\n\n"

    # For contests only: add contest link and created date
    # For problemsets: skip contest metadata (individual problems have their own links)
    if not is_pset:
        # Add contest link if available (extract from first problem link)
        if problems[0]['link']:
            first_link = problems[0]['link']
            if 'codeforces.com/group' in first_link:
                match = re.search(r'codeforces\.com/group/([^/]+)/contest/(\d+)', first_link)
                if match:
                    content += f"**Contest**: [Codeforces Group]({first_link.rsplit('/problem/', 1)[0]})\n\n"
            elif 'codeforces.com/contest' in first_link:
                contest_url = first_link.rsplit('/problem/', 1)[0]
                content += f"**Contest**: [Codeforces]({contest_url})\n\n"
            elif 'vjudge.net' in first_link:
                contest_url = first_link.rsplit('#problem/', 1)[0]
                content += f"**Contest**: [vJudge]({contest_url})\n\n"
            elif 'atcoder.jp' in first_link:
                match = re.search(r'atcoder\.jp/contests/([^/]+)', first_link)
                if match:
                    content += f"**Contest**: [AtCoder](https://atcoder.jp/contests/{match.group(1)})\n\n"

        # Add created date for contests
        created = problems[0]['created'] if problems[0]['created'] else datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        content += f"**Created**: {created}\n\n"

    # Statistics (for both contest and problemset)
    solved_count = sum(1 for p in problems if p['status'].lower() in ['solved', 'accepted', 'ac'])
    content += f"**Progress**: {solved_count}/{len(problems)} solved\n\n"

    # Problems table
    content += "## Problems\n\n"
    content += "| Problem | Status |\n"
    content += "|---------|--------|\n"

    for p in problems:
        # Get emoji for status
        emoji = get_status_emoji(p['status'])

        # Format problem title
        problem_title = p['problem'] if p['problem'] else p['char']

        # Format status label
        status_label = '' if p['status'] in ['~', ''] else p['status']

        # Add link if available
        if p['link']:
            content += f"| [{problem_title}]({p['link']}) | {emoji} {status_label} |\n"
        else:
            content += f"| {problem_title} | {emoji} {status_label} |\n"

    # Write info.md
    info_path = os.path.join(directory, "info.md")
    with open(info_path, 'w') as f:
        f.write(content)

    success(f"✓ Generated {info_path}")
    success(f"✓ Progress: {solved_count}/{len(problems)} solved")

ROOT_DIR = get_repo_root()

def update_all():
    """Recursively update info.md for all contest directories in the repo."""
    updated = 0
    for platform_dir in PLATFORM_DIRS:
        platform_path = os.path.join(ROOT_DIR, platform_dir)
        if not os.path.isdir(platform_path):
            continue

        for root, dirs, files in os.walk(platform_path):
            cpp_files = [f for f in files if f.endswith('.cpp')]
            if cpp_files:
                print()
                info(f"> {os.path.relpath(root, ROOT_DIR)}")
                generate_info_md(root)
                updated += 1

    if updated == 0:
        warning("No contest directories found.")
    else:
        print()
        bold(f"Updated {updated} contest(s).")

def get_parser():
    """Creates and returns the argparse parser for the update command."""
    parser = argparse.ArgumentParser(description="Generate or update info.md status file for the contest directory.")
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Target directory (default: current)')
    parser.add_argument('-a', '--all', action='store_true', help='Update all contest directories in the repository')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    if args.all:
        header("--- Updating All Contest Info ---")
        update_all()
        return

    directory = args.directory

    if not os.path.isdir(directory):
        error(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    header("--- Updating Contest Info ---")
    print(f"Directory: {directory}\n")

    generate_info_md(directory)
