#!/usr/bin/env python3
"""
Usage: cptools init [directory] [options]

Initialize a new competitive programming repository.
Creates platform directories, .gitignore, and ensures config exists.

Options:
  --no-git      Skip git initialization

Examples:
  cptools init
  cptools init my-cp-repo
  cptools init --no-git
"""
import os
import sys
import argparse
import subprocess

from lib.fileops import PLATFORM_DIRS
from lib.config import ensure_config, get_config_path
from lib.io import success, warning, info, header, bold

# Path to gitignore template
GITIGNORE_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'lib', 'templates', '.gitignore.template'
)

def get_parser():
    """Creates and returns the argparse parser for the init command."""
    parser = argparse.ArgumentParser(description="Initialize a new competitive programming repository.")
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Target directory')
    parser.add_argument('--no-git', action='store_true', dest='no_git', help='Skip git initialization')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()
    directory = args.directory

    header("--- Initializing contest repo ---")
    print(f"Directory: {directory}\n")

    os.makedirs(directory, exist_ok=True)

    # Create platform directories
    dirs_to_create = PLATFORM_DIRS + ['Codeforces/Gym', 'Codeforces/Problemset', 'AtCoder/Problemset']
    for d in dirs_to_create:
        path = os.path.join(directory, d)
        if not os.path.exists(path):
            os.makedirs(path)
            success(f"  + {d}/")
        else:
            warning(f"    {d}/ (already exists)")

    # Create .gitignore (only if git is enabled)
    if not args.no_git:
        gitignore_path = os.path.join(directory, ".gitignore")
        if not os.path.exists(gitignore_path):
            # Read from template
            with open(GITIGNORE_TEMPLATE_PATH, 'r') as f:
                gitignore_content = f.read()
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            success("  + .gitignore")
        else:
            warning("    .gitignore (already exists)")

    # Git init if not already a repo
    if not args.no_git:
        git_dir = os.path.join(directory, ".git")
        if not os.path.exists(git_dir):
            result = subprocess.run(
                ['git', 'init', directory],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print()
                success("  + git init")
            else:
                print()
                warning(f"  git init failed: {result.stderr.strip()}")
        else:
            warning("    .git/ (already a repo)")

    # Ensure config exists
    ensure_config()
    print()
    info(f"Config: {get_config_path()}")
    from lib.io import Colors
    print(f"Run {Colors.BOLD}cptools config{Colors.ENDC} to edit author name and settings.")

    print()
    bold("Done!")
