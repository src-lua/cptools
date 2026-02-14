#!/usr/bin/env python3
"""
Usage: cptools rm <problem>... [directory]

Remove problem files and their associated test cases.

Arguments:
  problem       Problem ID(s) to remove (e.g. A, B, dp_a, KQUERY.cpp)
                Supports ranges: A~E expands to A B C D E
  directory     Target directory (default: current)

Note:
  If the last argument is a directory path, it will be treated as
  the target directory. Otherwise, all arguments are treated as
  problem IDs and the current directory is used.
  The .cpp extension is optional and will be stripped automatically.

Examples:
  cptools rm A                        # Remove A from current directory
  cptools rm KQUERY.cpp               # Remove KQUERY (extension stripped)
  cptools rm dp_a dp_b                # Remove multiple problems from current directory
  cptools rm A B /path/to/contest     # Remove A and B from specific directory
  cptools rm 1636                     # Remove problem 1636 from current directory
  cptools rm A~E                      # Remove A, B, C, D, E from current directory
  cptools rm A~C /path/to/contest     # Remove A, B, C from specific directory
"""
import os
import sys
import argparse
import glob

from lib.io import success, warning, info, header, bold
from lib.parsing import parse_problem_range

def remove_problem(problem, directory):
    """Remove a problem file and its associated samples/binaries."""
    removed = []

    # Remove .cpp file
    cpp_file = os.path.join(directory, f"{problem}.cpp")
    if os.path.exists(cpp_file):
        os.remove(cpp_file)
        removed.append(f"{problem}.cpp")
    else:
        warning(f"  ! {problem}.cpp not found")
        return False

    # Remove sample test files (problem_*.in, problem_*.out)
    pattern_in = os.path.join(directory, f"{problem}_*.in")
    pattern_out = os.path.join(directory, f"{problem}_*.out")

    samples_in = glob.glob(pattern_in)
    samples_out = glob.glob(pattern_out)

    for f in samples_in + samples_out:
        os.remove(f)
        removed.append(os.path.basename(f))

    # Remove binary if it exists
    binary = os.path.join(directory, problem)
    if os.path.exists(binary):
        os.remove(binary)
        removed.append(problem)

    # Remove .hashed file if it exists (Q21)
    hashed_file = os.path.join(directory, f"{problem}.hashed")
    if os.path.exists(hashed_file):
        os.remove(hashed_file)
        removed.append(f"{problem}.hashed")

    # Print what was removed
    if removed:
        success(f"  - {problem}.cpp")
        if len(removed) > 1:
            info(f"    (+ {len(removed) - 1} related file(s))")

    return True

def get_parser():
    """Creates and returns the argparse parser for the rm command."""
    parser = argparse.ArgumentParser(description="Remove problem files and their associated test cases.")
    parser.add_argument('args', nargs='+', help='Problem ID(s) and optional directory')
    return parser

def run():
    parser = get_parser()
    opts = parser.parse_args()

    # Detect if last argument is a directory
    args = opts.args
    if len(args) > 1 and os.path.isdir(args[-1]):
        directory = args[-1]
        problem_args = args[:-1]
    else:
        directory = os.getcwd()
        problem_args = args

    # Expand ranges and collect all problems
    problems = []
    for arg in problem_args:
        # Strip .cpp extension if provided before parsing
        arg = arg.replace('.cpp', '') if arg.endswith('.cpp') else arg
        # Parse range (A~E) or single problem
        expanded = parse_problem_range(arg)
        problems.extend(expanded)

    # Remove duplicates while preserving order
    seen = set()
    problems = [p for p in problems if not (p in seen or seen.add(p))]

    # Safety confirmation for multiple problems
    if len(problems) > 3:
        print(f"You are about to remove {len(problems)} problems: {', '.join(problems[:10])}{' ...' if len(problems) > 10 else ''}")
        response = input("Are you sure? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Cancelled.")
            return

    header("--- Removing Problems ---")
    print()

    removed_count = 0
    for p in problems:
        if remove_problem(p, directory):
            removed_count += 1

    print()
    bold(f"Removed {removed_count}/{len(problems)} problem(s).")

    # Update info.md if there are still .cpp files remaining
    if removed_count > 0:
        cpp_files = [f for f in os.listdir(directory) if f.endswith('.cpp')]
        if cpp_files:
            try:
                from .update import generate_info_md
                generate_info_md(directory)
            except Exception:
                pass
        else:
            # Remove info.md if it exists and no .cpp files remain
            info_path = os.path.join(directory, "info.md")
            if os.path.exists(info_path):
                os.remove(info_path)
                info("Removed info.md (no problems remaining)")
