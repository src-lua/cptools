#!/usr/bin/env python3
"""
Fetch sample test cases from online judges.

Usage:
    cptools fetch <problem> [directory]
    cptools fetch A~E [directory]

Reads the Link from the problem's .cpp header and fetches sample
inputs/outputs, saving them as A1.in, A1.out, A2.in, A2.out, etc.
Supports Codeforces and AtCoder.
"""
import os
import sys

from .common import Colors
from lib import parse_problem_range, read_problem_header, save_samples, detect_judge

def fetch_problem(problem, directory):
    """Fetch samples for a single problem."""
    filename = f"{problem}.cpp"
    filepath = os.path.join(directory, filename)

    if not os.path.exists(filepath):
        print(f"  {Colors.WARNING}! {filename} not found{Colors.ENDC}")
        return False

    info = read_problem_header(filepath)
    if not info or not info.link:
        print(f"  {Colors.WARNING}! {filename} has no Link{Colors.ENDC}")
        return False

    url = info.link
    judge = detect_judge(url)
    if not judge:
        print(f"  {Colors.WARNING}! Unsupported platform for {filename}{Colors.ENDC}")
        return False

    samples = judge.fetch_samples(url)
    if not samples:
        print(f"  {Colors.WARNING}! No samples found for {filename}{Colors.ENDC}")
        return False

    # Convert SampleTest objects to dict format for save_samples
    samples_dict = [{'input': s.input, 'output': s.output} for s in samples]
    count = save_samples(directory, problem, samples_dict)
    print(f"  {Colors.GREEN}+ {problem}: {count} sample(s) saved{Colors.ENDC}")
    return True

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.FAIL}Usage: cptools fetch <problem(s)> [directory]{Colors.ENDC}")
        print(f"  Examples: cptools fetch A, cptools fetch A~E")
        sys.exit(1)

    problem_input = sys.argv[1]

    # Detect if argv[2] is a directory
    if len(sys.argv) > 2 and os.path.isdir(sys.argv[2]):
        directory = sys.argv[2]
    else:
        directory = os.getcwd()

    problems = parse_problem_range(problem_input)

    print(f"{Colors.HEADER}--- Fetching Samples ---{Colors.ENDC}\n")

    fetched = 0
    for p in problems:
        if fetch_problem(p, directory):
            fetched += 1

    print(f"\n{Colors.BOLD}Fetched {fetched}/{len(problems)} problem(s).{Colors.ENDC}")

if __name__ == "__main__":
    main()
