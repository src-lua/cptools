#!/usr/bin/env python3
"""
Usage: cptools mark <problem> [status] [directory]

Mark the status of a problem in its C++ header.

Arguments:
  problem       Problem ID or range (e.g. A, A~E, KQUERY.cpp)
  status        Status code (AC, WA, TLE, MLE, RE, WIP, ~) [default: AC]
  directory     Target directory (default: current)

Note:
  If only one extra argument is provided and it's a directory path,
  it will be treated as the directory and status will default to AC.
  The .cpp extension is optional and will be stripped automatically.

Examples:
  cptools mark A                        # Mark A as AC in current directory
  cptools mark KQUERY.cpp               # Mark KQUERY as AC (extension stripped)
  cptools mark A AC                     # Mark A as AC explicitly
  cptools mark A /path/to/contest       # Mark A as AC in specific directory
  cptools mark B WA /path/to/contest    # Mark B as WA in specific directory
  cptools mark A~E AC                   # Mark range A to E as AC
"""
import os
import sys
import argparse

from cptools.lib import parse_problem_range, update_problem_status
from cptools.lib.io import error, success, warning, info, bold
from cptools.lib.fileops import generate_header, read_problem_header
from cptools.lib.config import load_config

VALID_STATUSES = ['AC', 'WA', 'TLE', 'MLE', 'RE', 'WIP', '~']


def add_header_if_missing(filepath, problem_id, status='~'):
    """
    Add a header to a file that doesn't have one.

    Args:
        filepath: Path to .cpp file
        problem_id: Problem identifier
        status: Initial status

    Returns:
        True if header was added, False otherwise
    """
    config = load_config()
    author = config.get('author', 'Unknown')

    # Read existing content
    with open(filepath, 'r') as f:
        content = f.read()

    # Generate and prepend header
    header = generate_header(
        problem_id=problem_id,
        link='',
        problem_name=None,
        author=author,
        status=status
    )

    with open(filepath, 'w') as f:
        f.write(header)
        f.write(content)

    return True


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

    # Strip .cpp extension if provided (e.g., "KQUERY.cpp" -> "KQUERY")
    if problem_input.endswith('.cpp'):
        problem_input = problem_input[:-4]

    # Smart arg parsing: if first extra arg is a directory, treat it as the directory arg
    # BUT: Special case for '~' status - the shell expands ~ to home directory,
    # so we need to detect when the user meant the status '~' vs an actual directory
    home_dir = os.path.expanduser('~')
    is_tilde_status = (len(extra_args) == 1 and
                       extra_args[0] == home_dir and
                       os.path.isdir(extra_args[0]))

    if is_tilde_status:
        # User typed '~' which was expanded to home directory, but they meant the status
        new_status = '~'
        directory = os.getcwd()
    elif len(extra_args) > 0 and os.path.isdir(extra_args[0]):
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
            # File has no header - ask to add (default: yes)
            warning(f"  ! {p}.cpp has no cptools header")
            response = input(f"    Add header to {p}.cpp? (Y/n): ").strip().lower()
            if response in ['', 'y', 'yes']:
                # Convert underscores to spaces for display
                problem_display = p.replace('_', ' ')
                add_header_if_missing(filepath, problem_display, new_status)
                success(f"  + {p}: ~ -> {new_status} (header added)")
                updated += 1
            else:
                info(f"    Skipped {p}.cpp")
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
