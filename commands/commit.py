#!/usr/bin/env python3
"""
Commit and push contest or problem changes.

Usage:
    cptools commit [directory]
    cptools commit --all

Stages all changes in the contest directory, commits with a default
message (relative path from repo root), and pushes to remote.

With --all, walks every platform directory and commits each leaf
contest directory that has uncommitted changes as a separate commit,
then pushes once at the end.

Examples:
    cptools commit                 # commit current directory
    cptools commit Codeforces/2182 # commit specific contest
    cptools commit --all           # commit all changed contests
"""
import os
import sys
import subprocess

from .common import Colors, get_repo_root, PLATFORM_DIRS

def commit_directory(directory, root):
    """Stage and commit a single directory. Returns True if a commit was made."""
    rel_path = os.path.relpath(directory, root)

    # Stage changes
    result = subprocess.run(
        ['git', 'add', directory],
        capture_output=True, text=True, cwd=root
    )
    if result.returncode != 0:
        print(f"  {Colors.FAIL}! {rel_path}: staging failed{Colors.ENDC}")
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
        print(f"  {Colors.FAIL}! {rel_path}: commit failed{Colors.ENDC}")
        return False

    print(f"  {Colors.GREEN}+ {rel_path}{Colors.ENDC}")
    return True

def commit_all(root):
    """Walk platform directories and commit each contest directory individually."""
    print(f"{Colors.HEADER}--- Committing All ---{Colors.ENDC}\n")

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
        print(f"{Colors.WARNING}No changes to commit.{Colors.ENDC}")
        return

    print(f"\n{Colors.BOLD}Committed {committed} contest(s).{Colors.ENDC}")

    # Push once at the end
    result = subprocess.run(
        ['git', 'push'],
        capture_output=True, text=True, cwd=root
    )
    if result.returncode != 0:
        print(f"{Colors.WARNING}Push failed: {result.stderr.strip()}{Colors.ENDC}")
        print(f"{Colors.WARNING}Commits were created, but push failed.{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.GREEN}Pushed successfully.{Colors.ENDC}")

def main():
    root = get_repo_root()

    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        commit_all(root)
        return

    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    directory = os.path.abspath(directory)

    if not os.path.isdir(directory):
        print(f"{Colors.FAIL}Error: {directory} is not a valid directory.{Colors.ENDC}")
        sys.exit(1)

    rel_path = os.path.relpath(directory, root)
    if rel_path == '.':
        print(f"{Colors.FAIL}Error: run from inside a contest directory.{Colors.ENDC}")
        sys.exit(1)

    if not commit_directory(directory, root):
        print(f"{Colors.WARNING}No changes to commit.{Colors.ENDC}")
        sys.exit(0)

    # Push
    result = subprocess.run(
        ['git', 'push'],
        capture_output=True, text=True, cwd=root
    )
    if result.returncode != 0:
        print(f"{Colors.WARNING}Push failed: {result.stderr.strip()}{Colors.ENDC}")
        print(f"{Colors.WARNING}Commit was created, but push failed.{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.GREEN}Pushed successfully.{Colors.ENDC}")

if __name__ == "__main__":
    main()
