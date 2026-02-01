#!/usr/bin/env python3
"""
Open a problem's URL in the browser.

Usage:
    cptools open <problem> [directory]

Examples:
    cptools open A                  # opens A.cpp's Link in browser
    cptools open B /path/to/contest
"""
import os
import sys
import subprocess

from .common import Colors
from lib.fileops import read_problem_header, find_file_case_insensitive

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.FAIL}Usage: cptools open <problem> [directory]{Colors.ENDC}")
        sys.exit(1)

    problem = sys.argv[1]
    directory = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()

    filename = problem if problem.endswith('.cpp') else f"{problem}.cpp"
    match = find_file_case_insensitive(directory, filename)
    if match:
        filepath = os.path.join(directory, match)
        filename = match
    else:
        print(f"{Colors.FAIL}Error: {filename} not found.{Colors.ENDC}")
        sys.exit(1)

    header = read_problem_header(filepath)
    if not header or not header.link:
        print(f"{Colors.FAIL}Error: no Link found in {filename} header.{Colors.ENDC}")
        sys.exit(1)

    url = header.link
    print(f"{Colors.BLUE}Opening {url}{Colors.ENDC}")

    try:
        subprocess.Popen(
            ['xdg-open', url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print(f"{Colors.FAIL}Error: xdg-open not found.{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
