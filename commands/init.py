#!/usr/bin/env python3
"""
Initialize a new competitive programming repository.

Usage:
    cptools init [directory]             # default: current directory
    cptools init [directory] --nogit     # skip git init

Creates platform directories, .gitignore, and ensures config exists.
"""
import os
import sys
import subprocess

from .common import Colors, PLATFORM_DIRS
from .config import ensure_config, get_config_path

GITIGNORE_CONTENT = """\
__pycache__/
*.pyc
*.pyo

# Compiled binaries
*.out
*.o

# Stress test artifacts
_stress_*
"""

def main():
    nogit = '--nogit' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--nogit']
    directory = args[0] if args else os.getcwd()

    print(f"{Colors.HEADER}--- Initializing contest repo ---{Colors.ENDC}")
    print(f"Directory: {directory}\n")

    os.makedirs(directory, exist_ok=True)

    # Create platform directories
    dirs_to_create = PLATFORM_DIRS + ['Codeforces/Gym', 'Codeforces/Problemset', 'AtCoder/Problemset']
    for d in dirs_to_create:
        path = os.path.join(directory, d)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"  {Colors.GREEN}+ {d}/{Colors.ENDC}")
        else:
            print(f"  {Colors.WARNING}  {d}/ (already exists){Colors.ENDC}")

    # Create .gitignore
    gitignore_path = os.path.join(directory, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write(GITIGNORE_CONTENT)
        print(f"  {Colors.GREEN}+ .gitignore{Colors.ENDC}")
    else:
        print(f"  {Colors.WARNING}  .gitignore (already exists){Colors.ENDC}")

    # Git init if not already a repo
    if not nogit:
        git_dir = os.path.join(directory, ".git")
        if not os.path.exists(git_dir):
            result = subprocess.run(
                ['git', 'init', directory],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print(f"\n  {Colors.GREEN}+ git init{Colors.ENDC}")
            else:
                print(f"\n  {Colors.WARNING}git init failed: {result.stderr.strip()}{Colors.ENDC}")
        else:
            print(f"  {Colors.WARNING}  .git/ (already a repo){Colors.ENDC}")

    # Ensure config exists
    ensure_config()
    print(f"\n{Colors.BLUE}Config: {get_config_path()}{Colors.ENDC}")
    print(f"Run {Colors.BOLD}cptools config{Colors.ENDC} to edit author name and settings.")

    print(f"\n{Colors.BOLD}Done!{Colors.ENDC}")

if __name__ == "__main__":
    main()
