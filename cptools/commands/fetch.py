#!/usr/bin/env python3
"""
Usage: cptools fetch <problem> [directory]

Fetch sample test cases from online judges.
Reads the Link from the problem's .cpp header and fetches sample inputs/outputs.

Arguments:
  problem       Problem ID or range (e.g. A, A~E)
  directory     Target directory (default: current)

Examples:
  cptools fetch A
  cptools fetch A~E
"""
import os
import sys
import argparse

from cptools.lib import parse_problem_range, read_problem_header, save_samples, detect_judge, PlatformError
from cptools.lib.io import success, warning, header, bold, log, error

def fetch_problem(problem, directory):
    """Fetch samples for a single problem."""
    filename = f"{problem}.cpp"
    filepath = os.path.join(directory, filename)

    if not os.path.exists(filepath):
        warning(f"  ! {filename} not found")
        return False

    info = read_problem_header(filepath)
    if not info or not info.link:
        warning(f"  ! {filename} has no Link")
        return False

    url = info.link
    judge = detect_judge(url)
    if not judge:
        warning(f"  ! Unsupported platform for {filename}")
        return False

    try:
        samples = judge.fetch_samples(url)
        if not samples:
            warning(f"  ! No samples found for {filename}")
            return False

        # Convert SampleTest objects to dict format for save_samples
        samples_dict = [{'input': s.input, 'output': s.output} for s in samples]
        count = save_samples(directory, problem, samples_dict)
        success(f"  + {problem}: {count} sample(s) saved")
        return True
    except PlatformError as e:
        # Show authentication/platform errors with detailed message
        error(f"  ✗ {problem}: {str(e)}")
        return False

def get_parser():
    """Creates and returns the argparse parser for the fetch command."""
    parser = argparse.ArgumentParser(description="Fetch sample test cases from online judges.")
    parser.add_argument('problem', help='Problem ID or range (e.g. A, A~E)')
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Target directory (default: current)')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    directory = args.directory
    problems = parse_problem_range(args.problem)

    header("--- Fetching Samples ---")
    log("")  # blank line

    fetched = 0
    for p in problems:
        if fetch_problem(p, directory):
            fetched += 1

    bold(f"\nFetched {fetched}/{len(problems)} problem(s).")

