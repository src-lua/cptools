#!/usr/bin/env python3
"""
Compile and test a solution.

Usage:
    cptools test <problem> [directory]
    cptools test <problem> --add [--no-out]

Examples:
    cptools test A                  # compile & run A.cpp
    cptools test A < input.txt      # pipe input from file
    cptools test A                  # auto-tests if A_1.in exists (from cpt fetch)
    cptools test A --add            # add custom test, generate expected output
    cptools test A --add --no-out   # add custom test, skip output generation
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
    """Find sample files like A_1.in, A_2.in, etc. Handles gaps in numbering."""
    import re
    pattern = re.compile(rf'^{re.escape(problem)}_(\d+)\.in$')
    samples = []
    for f in os.listdir(directory):
        m = pattern.match(f)
        if m:
            num = int(m.group(1))
            in_file = os.path.join(directory, f)
            out_file = os.path.join(directory, f"{problem}_{num}.out")
            samples.append({
                'in': in_file,
                'out': out_file if os.path.exists(out_file) else None,
                'num': num,
            })
    samples.sort(key=lambda s: s['num'])
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

def next_test_index(directory, problem):
    """Find the next available test index."""
    i = 1
    while os.path.exists(os.path.join(directory, f"{problem}_{i}.in")):
        i += 1
    return i


def read_until_separator(label):
    """Read stdin until Ctrl+D, then reopen tty for next read."""
    eprint(f"{Colors.BLUE}{label} (Ctrl+D to finish):{Colors.ENDC}")
    data = sys.stdin.read()
    # Reopen tty so we can read again
    sys.stdin = open('/dev/tty', 'r')
    return data


def add_test(problem, directory, with_output):
    """Add a custom test case with the next available index."""
    idx = next_test_index(directory, problem)
    in_path = os.path.join(directory, f"{problem}_{idx}.in")
    out_path = os.path.join(directory, f"{problem}_{idx}.out")

    eprint(f"{Colors.HEADER}--- Adding Test {problem}_{idx} ---{Colors.ENDC}")

    input_data = read_until_separator("Input")

    with open(in_path, 'w') as f:
        f.write(input_data)
        if input_data and not input_data.endswith('\n'):
            f.write('\n')

    eprint(f"  {Colors.GREEN}+ {problem}_{idx}.in{Colors.ENDC}")

    if with_output:
        output_data = read_until_separator("Output")

        with open(out_path, 'w') as f:
            f.write(output_data)
            if output_data and not output_data.endswith('\n'):
                f.write('\n')

        eprint(f"  {Colors.GREEN}+ {problem}_{idx}.out{Colors.ENDC}")

    eprint(f"\n{Colors.BOLD}Test {problem}_{idx} added.{Colors.ENDC}")


def main():
    if len(sys.argv) < 2:
        eprint(f"{Colors.FAIL}Usage: cptools test <problem> [directory]{Colors.ENDC}")
        eprint(f"  cptools test <problem> --add [--no-out]")
        sys.exit(1)

    problem = sys.argv[1].replace('.cpp', '')

    add_mode = '--add' in sys.argv
    no_output = '--no-out' in sys.argv

    # Get directory: first non-flag arg after problem
    args = [a for a in sys.argv[2:] if not a.startswith('--')]
    directory = args[0] if args else os.getcwd()

    if add_mode:
        add_test(problem, directory, with_output=not no_output)
        return

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
