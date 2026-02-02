#!/usr/bin/env python3
"""
Usage: cptools open <problem> [directory]

Open a problem's URL in the default web browser.

Arguments:
  problem       Problem ID (e.g. A)
  directory     Target directory (default: current)

Examples:
  cptools open A
  cptools open B /path/to/contest
"""
import os
import sys
import argparse
import webbrowser

from lib.fileops import read_problem_header, find_file_case_insensitive
from lib.io import error, info

def get_parser():
    """Creates and returns the argparse parser for the open command."""
    parser = argparse.ArgumentParser(description="Open a problem's URL in the default web browser.")
    parser.add_argument('problem', help='Problem ID (e.g. A)')
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Target directory (default: current)')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    problem = args.problem
    directory = args.directory

    filename = problem if problem.endswith('.cpp') else f"{problem}.cpp"
    match = find_file_case_insensitive(directory, filename)
    if match:
        filepath = os.path.join(directory, match)
        filename = match
    else:
        error(f"Error: {filename} not found.")
        sys.exit(1)

    header = read_problem_header(filepath)
    if not header or not header.link:
        error(f"Error: no Link found in {filename} header.")
        sys.exit(1)

    url = header.link
    info(f"Opening {url}")

    webbrowser.open(url)
