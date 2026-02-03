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

from lib.fileops import read_problem_header, get_repo_root, PLATFORM_DIRS
from lib.io import error, success, warning, info, header, bold
from lib.display_utils import get_status_emoji
from lib.path_utils import detect_platform_from_path

def generate_info_md(directory):
    """Generate or update info.md for the contest directory."""
    directory = os.path.abspath(directory)

    # Find all .cpp files
    cpp_files = sorted([f for f in os.listdir(directory) if f.endswith('.cpp')])

    if not cpp_files:
        warning(f"No .cpp files found in {directory}")
        return

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

    # Generate markdown content
    content = f"# {platform}"
    if contest_id != Path(directory).name:
        content += f" - {contest_id}"
    content += "\n\n"

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
        elif 'judge.yosupo.jp' in first_link:
            content += f"**Judge**: [Yosupo Library Checker](https://judge.yosupo.jp)\n\n"

    # Add created date (from first problem or current time)
    created = problems[0]['created'] if problems[0]['created'] else datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    content += f"**Created**: {created}\n\n"

    # Statistics
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
