#!/usr/bin/env python3
"""
Compile and test a solution.

Usage:
    cptools test <problem> [directory]

Examples:
    cptools test A                  # compile & run A.cpp
    cptools test A < input.txt      # pipe input from file
    cptools test A                  # auto-tests if A1.in exists (from cpt fetch)
"""
import os
import sys
import subprocess

from .common import Colors
from .config import load_config


def eprint(*args, **kwargs):
    """Print to stderr so stdout redirection only captures solution output."""
    print(*args, file=sys.stderr, **kwargs)


def find_samples(directory, problem):
    """Find sample files like A_1.in, A_2.in, etc."""
    samples = []
    i = 1
    while True:
        in_file = os.path.join(directory, f"{problem}_{i}.in")
        if not os.path.exists(in_file):
            break
        out_file = os.path.join(directory, f"{problem}_{i}.out")
        samples.append({
            'in': in_file,
            'out': out_file if os.path.exists(out_file) else None,
            'num': i,
        })
        i += 1
    return samples

def compile_solution(source, binary, config):
    """Compile a C++ source file. Returns True on success."""
    compiler = config["compiler"]
    flags = config["compiler_flags"]
    cmd = [compiler] + flags + [source, "-o", binary]

    eprint(f"{Colors.BLUE}Compiling: {' '.join(cmd)}{Colors.ENDC}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        eprint(f"{Colors.FAIL}Compilation failed:{Colors.ENDC}")
        eprint(result.stderr)
        return False
    return True

def run_with_samples(binary, samples):
    """Run binary against sample test cases."""
    passed = 0
    total = len(samples)

    for sample in samples:
        with open(sample['in'], 'r') as f:
            input_data = f.read()

        result = subprocess.run(
            [binary],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=10,
        )

        actual = result.stdout.rstrip('\n')

        if sample['out']:
            with open(sample['out'], 'r') as f:
                expected = f.read().rstrip('\n')

            if actual == expected:
                eprint(f"  {Colors.GREEN}Sample {sample['num']}: PASS{Colors.ENDC}")
                passed += 1
            else:
                eprint(f"  {Colors.FAIL}Sample {sample['num']}: FAIL{Colors.ENDC}")
                eprint(f"    {Colors.BOLD}Input:{Colors.ENDC}")
                for line in input_data.strip().split('\n'):
                    eprint(f"      {line}")
                eprint(f"    {Colors.BOLD}Expected:{Colors.ENDC}")
                for line in expected.split('\n'):
                    eprint(f"      {line}")
                eprint(f"    {Colors.BOLD}Got:{Colors.ENDC}")
                for line in actual.split('\n'):
                    eprint(f"      {line}")
        else:
            eprint(f"  {Colors.BLUE}Sample {sample['num']}: (no expected output){Colors.ENDC}")
            eprint(f"    {Colors.BOLD}Output:{Colors.ENDC}")
            for line in actual.split('\n'):
                eprint(f"      {line}")
            passed += 1

    eprint(f"\n{Colors.BOLD}{passed}/{total} passed.{Colors.ENDC}")
    return passed == total

def main():
    if len(sys.argv) < 2:
        eprint(f"{Colors.FAIL}Usage: cptools test <problem> [directory]{Colors.ENDC}")
        sys.exit(1)

    problem = sys.argv[1].replace('.cpp', '')
    directory = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()

    source = os.path.join(directory, f"{problem}.cpp")
    if not os.path.exists(source):
        eprint(f"{Colors.FAIL}Error: {problem}.cpp not found.{Colors.ENDC}")
        sys.exit(1)

    config = load_config()
    binary = os.path.join(directory, f".{problem}")

    if not compile_solution(source, binary, config):
        sys.exit(1)

    try:
        samples = find_samples(directory, problem)

        if samples and sys.stdin.isatty():
            eprint(f"{Colors.BLUE}Running {len(samples)} sample(s)...{Colors.ENDC}\n")
            success = run_with_samples(binary, samples)
            sys.exit(0 if success else 1)
        else:
            # Interactive mode or piped stdin
            if not sys.stdin.isatty():
                result = subprocess.run([binary], stdin=sys.stdin)
            else:
                eprint(f"{Colors.BLUE}Running interactively (Ctrl+D to end input)...{Colors.ENDC}")
                result = subprocess.run([binary])
            sys.exit(result.returncode)
    except subprocess.TimeoutExpired:
        eprint(f"{Colors.FAIL}Time limit exceeded (10s){Colors.ENDC}")
        sys.exit(1)
    finally:
        if os.path.exists(binary):
            os.remove(binary)

if __name__ == "__main__":
    main()
