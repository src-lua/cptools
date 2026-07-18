#!/usr/bin/env python3
"""
Usage: cptools clean [directory] [options]

Delete compiled binaries and build artifacts from contest directories.

Options:
  -r, --recursive    Recursive clean (subdirectories)
  -a, --all          Clean all platform directories in the repo

Examples:
  cptools clean
  cptools clean -r
  cptools clean -a
"""
import os
import sys
import shutil
import argparse

from cptools.lib.fileops import is_removable, get_repo_root, PLATFORM_DIRS
from cptools.lib.io import error, bold, log

ROOT_DIR = get_repo_root()

def clean_directory(directory, recursive=False):
    """Remove binaries, build artifacts, and .dSYM bundles from a directory."""
    removed = 0
    if recursive:
        walker = os.walk(directory)
    else:
        try:
            entries = os.listdir(directory)
            subdirs = [e for e in entries if os.path.isdir(os.path.join(directory, e))]
            files = [e for e in entries if os.path.isfile(os.path.join(directory, e))]
            walker = [(directory, subdirs, files)]
        except OSError:
            return 0

    for root, dirs, files in walker:
        if recursive:
            dirs[:] = [d for d in dirs if not d.startswith('.')]

        # Remove .dSYM bundles (Mac debug symbol directories)
        for d in list(dirs):
            if d.endswith('.dSYM'):
                dirpath = os.path.join(root, d)
                rel = os.path.relpath(dirpath, ROOT_DIR)
                try:
                    shutil.rmtree(dirpath)
                    log(f"  - {rel}/")
                    removed += 1
                    dirs.remove(d)
                except OSError as e:
                    log(f"  Error deleting {rel}: {e}")

        for f in files:
            filepath = os.path.join(root, f)
            if os.path.isfile(filepath) and is_removable(filepath):
                rel = os.path.relpath(filepath, ROOT_DIR)
                try:
                    os.remove(filepath)
                    log(f"  - {rel}")
                    removed += 1
                except OSError as e:
                    log(f"  Error deleting {rel}: {e}")
    return removed

def get_parser():
    """Creates and returns the argparse parser for the clean command."""
    parser = argparse.ArgumentParser(description="Delete compiled binaries and build artifacts from contest directories.")
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Target directory (default: current)')
    parser.add_argument('-r', '--recursive', action='store_true', dest='recursive', help='Recursive clean (subdirectories)')
    parser.add_argument('-a', '--all', action='store_true', help='Clean all platform directories in the repo')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    if args.all:
        total = 0
        for d in PLATFORM_DIRS:
            path = os.path.join(ROOT_DIR, d)
            if os.path.isdir(path):
                total += clean_directory(path, recursive=True)
        bold(f"\nRemoved {total} file(s).")
    else:
        recursive = args.recursive
        directory = args.directory
        if not os.path.isdir(directory):
            error(f"Error: {directory} is not a valid directory.")
            sys.exit(1)
        removed = clean_directory(directory, recursive=recursive)
        bold(f"\nRemoved {removed} file(s).")
