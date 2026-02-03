#!/usr/bin/env python3
"""
Usage: cptools mark <problem> [status] [directory]

Mark the status of a problem in its C++ header.

Arguments:
  problem       Problem ID or range (e.g. A, A~E)
  status        Status code (AC, WA, TLE, MLE, RE, WIP, ~) [default: AC]
  directory     Target directory (default: current)

Examples:
  cptools mark A
  cptools mark A AC
  cptools mark B WA /path/to/contest
  cptools mark A~E AC
"""
import os
import sys
import argparse

from lib import parse_problem_range, update_problem_status
from lib.io import error, success, warning, info, bold

VALID_STATUSES = ['AC', 'WA', 'TLE', 'MLE', 'RE', 'WIP', '~']

def get_parser():
    """Creates and returns the argparse parser for the mark command."""
    parser = argparse.ArgumentParser(description="Mark the status of a problem in its C++ header.")
    parser.add_argument('problem', help='Problem ID or range (e.g. A, A~E)')
    parser.add_argument('args', nargs='*', help='Status code and/or directory')
    return parser

def run():
    parser = get_parser()
    opts = parser.parse_args()

    problem_input = opts.problem
    extra_args = opts.args

    # Smart arg parsing: if first extra arg is a directory, treat it as the directory arg
    if len(extra_args) > 0 and os.path.isdir(extra_args[0]):
        new_status = 'AC'
        directory = extra_args[0]
    else:
        new_status = extra_args[0].upper() if len(extra_args) > 0 else 'AC'
        directory = extra_args[1] if len(extra_args) > 1 else os.getcwd()

    if new_status not in VALID_STATUSES:
        warning(f"Warning: '{new_status}' is not a standard status.")
        print(f"  Standard: {', '.join(VALID_STATUSES)}")

    problems = parse_problem_range(problem_input)

    updated = 0
    for p in problems:
        filepath = os.path.join(directory, f"{p}.cpp")
        if not os.path.exists(filepath):
            warning(f"  ! {p}.cpp not found")
            continue

        old_status = update_problem_status(filepath, new_status)
        if old_status is None:
            warning(f"  ! {p}.cpp has no Status header")
        else:
            success(f"  + {p}: {old_status} -> {new_status}")
            updated += 1

    if updated > 0:
        print()
        info("Updating info.md...")
        from .update import generate_info_md
        generate_info_md(directory)

    print()
    bold(f"Updated {updated}/{len(problems)} problem(s).")
