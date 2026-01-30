#!/usr/bin/env python3
"""
Mark the status of a problem in its C++ header.

Usage:
    python3 mark_status.py <problem> [status] [directory]

Examples:
    python3 mark_status.py A                   # defaults to AC
    python3 mark_status.py A AC
    python3 mark_status.py B WA /path/to/contest
    python3 mark_status.py A~E AC              # mark multiple problems

Valid statuses: AC, WA, TLE, MLE, RE, WIP, ~ (reset to pending)
"""
import os
import sys
import re

from .common import Colors

VALID_STATUSES = ['AC', 'WA', 'TLE', 'MLE', 'RE', 'WIP', '~']

def parse_problems(input_str):
    input_str = input_str.upper()
    if '~' in input_str:
        parts = input_str.split('~')
        if len(parts) == 2 and len(parts[0].strip()) == 1 and len(parts[1].strip()) == 1:
            start = ord(parts[0].strip())
            end = ord(parts[1].strip())
            return [chr(i) for i in range(start, end + 1)]
    return input_str.replace(',', ' ').split()

def update_status(filepath, new_status):
    with open(filepath, 'r') as f:
        content = f.read()

    pattern = r'(\* Status:\s*)([^\n]*)'
    match = re.search(pattern, content)
    if not match:
        return False

    old_status = match.group(2).strip()
    updated = re.sub(pattern, rf'\g<1>{new_status}', content)

    with open(filepath, 'w') as f:
        f.write(updated)

    return old_status

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.FAIL}Usage: mark_status.py <problem(s)> [status] [directory]{Colors.ENDC}")
        print(f"  Problems: A, B, A~E, \"A B C\"")
        print(f"  Statuses: {', '.join(VALID_STATUSES)} (default: AC)")
        sys.exit(1)

    problem_input = sys.argv[1]

    # Smart arg parsing: if argv[2] is a directory, treat it as the directory arg
    if len(sys.argv) > 2 and os.path.isdir(sys.argv[2]):
        new_status = 'AC'
        directory = sys.argv[2]
    else:
        new_status = sys.argv[2].upper() if len(sys.argv) > 2 else 'AC'
        directory = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()

    if new_status not in VALID_STATUSES:
        print(f"{Colors.WARNING}Warning: '{new_status}' is not a standard status.{Colors.ENDC}")
        print(f"  Standard: {', '.join(VALID_STATUSES)}")

    problems = parse_problems(problem_input)

    updated = 0
    for p in problems:
        filepath = os.path.join(directory, f"{p}.cpp")
        if not os.path.exists(filepath):
            print(f"  {Colors.WARNING}! {p}.cpp not found{Colors.ENDC}")
            continue

        old_status = update_status(filepath, new_status)
        if old_status is False:
            print(f"  {Colors.WARNING}! {p}.cpp has no Status header{Colors.ENDC}")
        else:
            print(f"  {Colors.GREEN}+ {p}: {old_status} -> {new_status}{Colors.ENDC}")
            updated += 1

    if updated > 0:
        print(f"\n{Colors.BLUE}Updating info.md...{Colors.ENDC}")
        from .update_info import generate_info_md
        generate_info_md(directory)

    print(f"\n{Colors.BOLD}Updated {updated}/{len(problems)} problem(s).{Colors.ENDC}")

if __name__ == "__main__":
    main()
