#!/usr/bin/env python3
"""
Usage: cptools add-header <file> [options]

Add a cptools header to an existing C++ file that doesn't have one.

Arguments:
  file          Path to .cpp file

Options:
  -l, --link    Problem URL
  -n, --name    Problem name
  -s, --status  Initial status (default: ~)
  -f, --force   Overwrite existing header

Examples:
  cptools add-header A.cpp
  cptools add-header solution.cpp --name "Two Sum" --link "https://..."
  cptools add-header old.cpp --force
"""
import os
import argparse
from datetime import datetime

from lib.fileops import generate_header, read_problem_header
from lib.io import success, warning, error, info
from lib.config import load_config


def has_header(filepath):
    """Check if file already has a cptools header."""
    try:
        header = read_problem_header(filepath)
        # A file has a header if at least the problem field was found
        return header is not None and header.problem is not None
    except Exception:
        return False


def add_header_to_file(filepath, problem_id, link="", problem_name=None, status="~", force=False):
    """
    Add a header to an existing C++ file.

    Args:
        filepath: Path to .cpp file
        problem_id: Problem identifier
        link: Problem URL (optional)
        problem_name: Problem name (optional)
        status: Initial status (default: ~)
        force: Overwrite existing header if present

    Returns:
        True if header was added, False otherwise
    """
    if not os.path.exists(filepath):
        error(f"File not found: {filepath}")
        return False

    # Check for existing header
    if has_header(filepath) and not force:
        warning(f"File already has a header: {filepath}")
        info("Use --force to overwrite the existing header")
        return False

    # Read existing content
    with open(filepath, 'r') as f:
        content = f.read()

    # Get author from config
    config = load_config()
    author = config.get('author', 'Unknown')

    # Generate header
    header = generate_header(
        problem_id=problem_id,
        link=link,
        problem_name=problem_name,
        author=author,
        status=status
    )

    # If force and has existing header, remove it
    if force and has_header(filepath):
        # Find and remove existing header
        lines = content.split('\n')
        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if line.strip().startswith('/**'):
                start_idx = i
            elif start_idx is not None and line.strip().endswith('**/'):
                end_idx = i
                break

        if start_idx is not None and end_idx is not None:
            # Remove old header and any blank lines after it
            del lines[start_idx:end_idx + 1]
            while lines and lines[0].strip() == '':
                del lines[0]
            content = '\n'.join(lines)

    # Write new header + content
    with open(filepath, 'w') as f:
        f.write(header)
        f.write(content)

    return True


def get_parser():
    """Creates and returns the argparse parser for the add-header command."""
    parser = argparse.ArgumentParser(
        description="Add a cptools header to an existing C++ file."
    )
    parser.add_argument('file', help='Path to .cpp file')
    parser.add_argument('-l', '--link', default='', help='Problem URL')
    parser.add_argument('-n', '--name', help='Problem name')
    parser.add_argument('-s', '--status', default='~', help='Initial status (default: ~)')
    parser.add_argument('-f', '--force', action='store_true',
                       help='Overwrite existing header')
    return parser


def run():
    parser = get_parser()
    opts = parser.parse_args()

    filepath = opts.file

    # Extract problem ID from filename
    basename = os.path.basename(filepath)
    if basename.endswith('.cpp'):
        problem_id = basename[:-4]
    else:
        problem_id = basename

    # Convert underscores to spaces for display (e.g., "word_other" -> "word other")
    problem_display = problem_id.replace('_', ' ')

    # Add header
    if add_header_to_file(
        filepath=filepath,
        problem_id=problem_display,
        link=opts.link,
        problem_name=opts.name,
        status=opts.status,
        force=opts.force
    ):
        success(f"✓ Added header to {filepath}")
    else:
        error(f"✗ Failed to add header to {filepath}")
