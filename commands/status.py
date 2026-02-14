#!/usr/bin/env python3
"""
Usage: cptools status [directory]

Show a quick summary of the current contest directory.

Arguments:
  directory     Target directory (default: current)

Examples:
  cptools status
  cptools status /path/to/contest
"""
import os
import sys
import argparse
from lib.display_utils import get_status_emoji
from lib.fileops import read_problem_header, generate_header
from lib.io import error, warning, Colors, log, info
from lib.config import load_config

def get_parser():
    """Creates and returns the argparse parser for the status command."""
    parser = argparse.ArgumentParser(description="Show a quick summary of the current contest directory.")
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Target directory (default: current)')
    return parser

def add_header_to_file(filepath, problem_id):
    """Add a header to a file that doesn't have one."""
    config = load_config()
    author = config.get('author', 'Unknown')

    with open(filepath, 'r') as f:
        content = f.read()

    header = generate_header(
        problem_id=problem_id,
        link='',
        problem_name=None,
        author=author,
        status='~'
    )

    with open(filepath, 'w') as f:
        f.write(header)
        f.write(content)


def run():
    parser = get_parser()
    args = parser.parse_args()

    directory = args.directory

    if not os.path.isdir(directory):
        error(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    cpp_files = sorted([f for f in os.listdir(directory) if f.endswith('.cpp')])
    if not cpp_files:
        warning("No .cpp files found.")
        sys.exit(1)

    # Check for files without headers
    files_without_headers = []
    for cpp_file in cpp_files:
        filepath = os.path.join(directory, cpp_file)
        header = read_problem_header(filepath)
        if not header or header.problem is None:
            files_without_headers.append(cpp_file)

    # Offer to add headers if any files are missing them
    if files_without_headers:
        warning(f"Found {len(files_without_headers)} file(s) without cptools headers:")
        for f in files_without_headers:
            info(f"  • {f}")
        response = input("\nAdd headers to these files? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            for cpp_file in files_without_headers:
                filepath = os.path.join(directory, cpp_file)
                problem_id = cpp_file.replace('.cpp', '')
                # Convert underscores to spaces for display
                problem_display = problem_id.replace('_', ' ')
                add_header_to_file(filepath, problem_display)
                info(f"  ✓ Added header to {cpp_file}")
            print()

    counts = {}
    problems = []
    for cpp_file in cpp_files:
        filepath = os.path.join(directory, cpp_file)
        header = read_problem_header(filepath)
        if not header or header.problem is None:
            continue

        status = header.status.upper().strip()
        if status in ['~', '']:
            status = '~'
        counts[status] = counts.get(status, 0) + 1

        char = cpp_file.replace('.cpp', '')
        emoji = get_status_emoji(header.status)
        name = header.problem if header.problem else char
        problems.append((char, emoji, header.status, name))

    total = len(problems)
    ac = counts.get('AC', 0) + counts.get('SOLVED', 0) + counts.get('ACCEPTED', 0)

    # Header
    dirname = os.path.basename(os.path.abspath(directory))
    log(f"{Colors.BOLD}{dirname}{Colors.ENDC}  {ac}/{total} solved\n")

    # Problem list
    for char, emoji, status, name in problems:
        label = '' if status in ['~', ''] else f" {status}"
        log(f"  {emoji}{label:<5} {Colors.BOLD}{char:<4}{Colors.ENDC} {name}")

    # Summary line
    log()
    parts = []
    if ac > 0:
        parts.append(f"{Colors.GREEN}{ac} AC{Colors.ENDC}")
    for key in ['WA', 'TLE', 'MLE', 'RE', 'WIP']:
        if counts.get(key, 0) > 0:
            parts.append(f"{Colors.WARNING}{counts[key]} {key}{Colors.ENDC}")
    pending = counts.get('~', 0)
    if pending > 0:
        parts.append(f"{pending} pending")
    log("  " + "  ".join(parts))
