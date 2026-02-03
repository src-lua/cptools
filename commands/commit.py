#!/usr/bin/env python3
"""
Usage: cptools commit [directory] [options]

Commit and push contest or problem changes.
Stages changes, commits with default message, and pushes to remote.

Options:
  -a, --all     Commit all changed contests in the repository

Examples:
  cptools commit
  cptools commit Codeforces/1234
  cptools commit -a
"""
import os
import sys
import argparse
import subprocess

from lib.fileops import get_repo_root, PLATFORM_DIRS
from lib.io import error, success, warning, header, bold

def commit_directory(directory, root):
    """Stage and commit a single directory. Returns True if a commit was made."""
    rel_path = os.path.relpath(directory, root)

    # Stage changes
    result = subprocess.run(
        ['git', 'add', directory],
        capture_output=True, text=True, cwd=root
    )
    if result.returncode != 0:
        error(f"  ! {rel_path}: staging failed")
        return False

    # Check if there are staged changes
    result = subprocess.run(
        ['git', 'diff', '--cached', '--quiet'],
        capture_output=True, text=True, cwd=root
    )
    if result.returncode == 0:
        return False

    # Commit
    result = subprocess.run(
        ['git', 'commit', '-m', rel_path],
        capture_output=True, text=True, cwd=root
    )
    if result.returncode != 0:
        error(f"  ! {rel_path}: commit failed")
        return False

    success(f"  + {rel_path}")
    return True

def commit_all(root):
    """Walk platform directories and commit each contest directory individually."""
    header("--- Committing All ---")
    print()

    committed = 0
    for platform_dir in PLATFORM_DIRS:
        platform_path = os.path.join(root, platform_dir)
        if not os.path.isdir(platform_path):
            continue

        for dirpath, dirs, files in os.walk(platform_path):
            cpp_files = [f for f in files if f.endswith('.cpp')]
            if cpp_files:
                dirs.clear()  # don't descend further into this contest
                if commit_directory(dirpath, root):
                    committed += 1

    if committed == 0:
        warning("No changes to commit.")
        return

    print()
    bold(f"Committed {committed} contest(s).")

    # Push once at the end
    result = subprocess.run(
        ['git', 'push'],
        capture_output=True, text=True, cwd=root
    )
    if result.returncode != 0:
        warning(f"Push failed: {result.stderr.strip()}")
        warning("Commits were created, but push failed.")
        sys.exit(1)

    success("Pushed successfully.")

def get_parser():
    """Creates and returns the argparse parser for the commit command."""
    parser = argparse.ArgumentParser(description="Commit and push contest or problem changes.")
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Target directory')
    parser.add_argument('-a', '--all', action='store_true', help='Commit all changed contests in the repository')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()
    
    root = get_repo_root()

    if args.all:
        commit_all(root)
        return

    directory = os.path.abspath(args.directory)

    if not os.path.isdir(directory):
        error(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    rel_path = os.path.relpath(directory, root)
    if rel_path == '.':
        error("Error: run from inside a contest directory.")
        sys.exit(1)

    if not commit_directory(directory, root):
        warning("No changes to commit.")
        sys.exit(0)

    # Push
    result = subprocess.run(
        ['git', 'push'],
        capture_output=True, text=True, cwd=root
    )
    if result.returncode != 0:
        warning(f"Push failed: {result.stderr.strip()}")
        warning("Commit was created, but push failed.")
        sys.exit(1)

    success("Pushed successfully.")
