#!/usr/bin/env python3
"""
Delete compiled binaries and build artifacts from contest directories.

Usage:
    cptools clean [directory]      # clean specific directory (non-recursive)
    cptools clean -r [directory]   # clean directory recursively
    cptools clean --all            # clean all platform directories (recursive)
"""
import os
import sys

from .common import Colors, get_repo_root, PLATFORM_DIRS

ROOT_DIR = get_repo_root()

SAFE_FILES = {'LICENSE', 'Makefile', 'CNAME', 'README'}

BUILD_EXTENSIONS = {'.out', '.o', '.in'}

def is_removable(filepath):
    """Check if a file is a compiled binary or build artifact."""
    name = os.path.basename(filepath)

    if name.startswith('_') or name.startswith('.'):
        return False

    if name in SAFE_FILES:
        return False

    _, ext = os.path.splitext(name)

    # Build artifacts and test files by extension
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

def clean_directory(directory, recursive=False):
    """Remove binaries and build artifacts from a directory."""
    removed = 0
    if recursive:
        entries = os.walk(directory)
    else:
        entries = [(directory, [], os.listdir(directory))]

    for root, dirs, files in entries:
        if recursive:
            dirs[:] = [d for d in dirs if not d.startswith('.')]

        for f in files:
            filepath = os.path.join(root, f)
            if os.path.isfile(filepath) and is_removable(filepath):
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
                total += clean_directory(path, recursive=True)
        print(f"\n{Colors.BOLD}Removed {total} file(s).{Colors.ENDC}")
    else:
        recursive = '-r' in sys.argv
        args = [a for a in sys.argv[1:] if a != '-r']
        directory = args[0] if args else os.getcwd()
        if not os.path.isdir(directory):
            print(f"{Colors.FAIL}Error: {directory} is not a valid directory.{Colors.ENDC}")
            sys.exit(1)
        removed = clean_directory(directory, recursive=recursive)
        print(f"\n{Colors.BOLD}Removed {removed} file(s).{Colors.ENDC}")

if __name__ == "__main__":
    main()