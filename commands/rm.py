#!/usr/bin/env python3
"""
Remove problem files and their associated test cases.

Usage:
    cptools rm <problem> [directory]
    cptools rm A B C [directory]

Examples:
    cptools rm A                    # removes A.cpp and A_*.in/out in current dir
    cptools rm dp_a dp_b            # removes multiple problems
    cptools rm 1636                 # removes CSES problem 1636
"""
import os
import sys
import glob

from .common import Colors

def remove_problem(problem, directory):
    """Remove a problem file and its associated samples/binaries."""
    removed = []

    # Remove .cpp file
    cpp_file = os.path.join(directory, f"{problem}.cpp")
    if os.path.exists(cpp_file):
        os.remove(cpp_file)
        removed.append(f"{problem}.cpp")
    else:
        print(f"  {Colors.WARNING}! {problem}.cpp not found{Colors.ENDC}")
        return False

    # Remove sample test files (problem_*.in, problem_*.out)
    pattern_in = os.path.join(directory, f"{problem}_*.in")
    pattern_out = os.path.join(directory, f"{problem}_*.out")

    samples_in = glob.glob(pattern_in)
    samples_out = glob.glob(pattern_out)

    for f in samples_in + samples_out:
        os.remove(f)
        removed.append(os.path.basename(f))

    # Remove binary if it exists
    binary = os.path.join(directory, problem)
    if os.path.exists(binary):
        os.remove(binary)
        removed.append(problem)

    # Print what was removed
    if removed:
        print(f"  {Colors.GREEN}- {problem}.cpp{Colors.ENDC}")
        if len(removed) > 1:
            print(f"    {Colors.BLUE}(+ {len(removed) - 1} related file(s)){Colors.ENDC}")

    return True

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.FAIL}Usage: cptools rm <problem(s)> [directory]{Colors.ENDC}")
        print(f"  Examples: cptools rm A, cptools rm A B C")
        sys.exit(1)

    # Detect if last argument is a directory
    args = sys.argv[1:]
    if len(args) > 1 and os.path.isdir(args[-1]):
        directory = args[-1]
        problems = args[:-1]
    else:
        directory = os.getcwd()
        problems = args

    print(f"{Colors.HEADER}--- Removing Problems ---{Colors.ENDC}\n")

    removed_count = 0
    for p in problems:
        if remove_problem(p, directory):
            removed_count += 1

    print(f"\n{Colors.BOLD}Removed {removed_count}/{len(problems)} problem(s).{Colors.ENDC}")

    # Update info.md if it exists
    if removed_count > 0:
        try:
            from .update import generate_info_md
            generate_info_md(directory)
        except Exception:
            pass

if __name__ == "__main__":
    main()
