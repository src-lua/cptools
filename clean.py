#!/usr/bin/env python3
"""
Delete compiled binaries and build artifacts from contest directories.

Usage:
    python3 clean.py [directory]   # clean specific directory
    python3 clean.py --all         # clean all platform directories
    python3 clean.py               # clean current directory
"""
import os
import sys

from colors import Colors, get_repo_root

ROOT_DIR = get_repo_root()

PLATFORM_DIRS = ['training', 'Codeforces', 'VJudge', 'AtCoder', 'Other', 'summer']

SAFE_FILES = {'LICENSE', 'Makefile', 'CNAME', 'README'}

BUILD_EXTENSIONS = {'.out', '.o'}

def is_removable(filepath):
    """Check if a file is a compiled binary or build artifact."""
    name = os.path.basename(filepath)

    if name.startswith('_') or name.startswith('.'):
        return False

    if name in SAFE_FILES:
        return False

    _, ext = os.path.splitext(name)

    # Build artifacts by extension
    if ext in BUILD_EXTENSIONS:
        return True

    # Extensionless binary detection
    if ext != '':
        return False

    try:
        with open(filepath, 'rb') as f:
            header = f.read(2)
            if header == b'#!':
                return False
    except (IOError, OSError):
        pass

    return True

def clean_directory(directory):
    """Remove binaries and build artifacts from a directory tree."""
    removed = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for f in files:
            filepath = os.path.join(root, f)
            if is_removable(filepath):
                rel = os.path.relpath(filepath, ROOT_DIR)
                try:
                    os.remove(filepath)
                    print(f"  {Colors.FAIL}- {rel}{Colors.ENDC}")
                    removed += 1
                except OSError as e:
                    print(f"  Error deleting {rel}: {e}")
    return removed

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        total = 0
        for d in PLATFORM_DIRS:
            path = os.path.join(ROOT_DIR, d)
            if os.path.isdir(path):
                total += clean_directory(path)
        print(f"\n{Colors.BOLD}Removed {total} file(s).{Colors.ENDC}")
    else:
        directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
        if not os.path.isdir(directory):
            print(f"{Colors.FAIL}Error: {directory} is not a valid directory.{Colors.ENDC}")
            sys.exit(1)
        removed = clean_directory(directory)
        print(f"\n{Colors.BOLD}Removed {removed} file(s).{Colors.ENDC}")

if __name__ == "__main__":
    main()