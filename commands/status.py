#!/usr/bin/env python3
"""
Show a quick summary of the current contest directory.

Usage:
    python3 contest_status.py [directory]
"""
import os
import sys
from .common import Colors
from .update import get_status_emoji
from lib.fileops import read_problem_header

def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    if not os.path.isdir(directory):
        print(f"{Colors.FAIL}Error: {directory} is not a valid directory.{Colors.ENDC}")
        sys.exit(1)

    cpp_files = sorted([f for f in os.listdir(directory) if f.endswith('.cpp')])
    if not cpp_files:
        print(f"{Colors.WARNING}No .cpp files found.{Colors.ENDC}")
        sys.exit(1)

    counts = {}
    problems = []
    for cpp_file in cpp_files:
        filepath = os.path.join(directory, cpp_file)
        header = read_problem_header(filepath)
        if not header:
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
    print(f"{Colors.BOLD}{dirname}{Colors.ENDC}  {ac}/{total} solved\n")

    # Problem list
    for char, emoji, status, name in problems:
        label = '' if status in ['~', ''] else f" {status}"
        print(f"  {emoji}{label:<5} {Colors.BOLD}{char:<4}{Colors.ENDC} {name}")

    # Summary line
    print()
    parts = []
    if ac > 0:
        parts.append(f"{Colors.GREEN}{ac} AC{Colors.ENDC}")
    for key in ['WA', 'TLE', 'MLE', 'RE', 'WIP']:
        if counts.get(key, 0) > 0:
            parts.append(f"{Colors.WARNING}{counts[key]} {key}{Colors.ENDC}")
    pending = counts.get('~', 0)
    if pending > 0:
        parts.append(f"{pending} pending")
    print("  " + "  ".join(parts))

if __name__ == "__main__":
    main()
