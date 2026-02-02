#!/usr/bin/env python3
"""
Usage: cptools test <problem> [directory] [options]

Compile and test a solution against samples or custom inputs.

Options:
  --add         Add a new custom test case
  --no-out      Skip generating expected output (when adding test)

Examples:
  cptools test A
  cptools test A --add
  cptools test A --add --no-out
"""
import os
import sys
import argparse
import subprocess

from lib.config import load_config
from lib import find_samples, compile_from_config, next_test_index
from lib.io import log, error, success, info, header, bold

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
                success(f"  Sample {sample['num']}: PASS")
                passed += 1
            else:
                error(f"  Sample {sample['num']}: FAIL")
                bold("    Input:")
                for line in input_data.strip().split('\n'):
                    log(f"      {line}")
                bold("    Expected:")
                for line in expected.split('\n'):
                    log(f"      {line}")
                bold("    Got:")
                for line in actual.split('\n'):
                    log(f"      {line}")
        else:
            info(f"  Sample {sample['num']}: (no expected output)")
            bold("    Output:")
            for line in actual.split('\n'):
                log(f"      {line}")
            passed += 1

    bold(f"\n{passed}/{total} passed.")
    return passed == total


def read_until_separator(label):
    """Read stdin until Ctrl+D, then reopen tty for next read."""
    info(f"{label} (Ctrl+D to finish):")
    data = sys.stdin.read()
    # Reopen tty so we can read again
    sys.stdin = open('/dev/tty', 'r')
    return data


def add_test(problem, directory, with_output):
    """Add a custom test case with the next available index."""
    idx = next_test_index(directory, problem)
    in_path = os.path.join(directory, f"{problem}_{idx}.in")
    out_path = os.path.join(directory, f"{problem}_{idx}.out")

    header(f"--- Adding Test {problem}_{idx} ---")

    input_data = read_until_separator("Input")

    with open(in_path, 'w') as f:
        f.write(input_data)
        if input_data and not input_data.endswith('\n'):
            f.write('\n')

    success(f"  + {problem}_{idx}.in")

    if with_output:
        output_data = read_until_separator("Output")

        with open(out_path, 'w') as f:
            f.write(output_data)
            if output_data and not output_data.endswith('\n'):
                f.write('\n')

        success(f"  + {problem}_{idx}.out")

    bold(f"\nTest {problem}_{idx} added.")


def get_parser():
    """Creates and returns the argparse parser for the test command."""
    parser = argparse.ArgumentParser(description="Compile and test a solution against samples or custom inputs.")
    parser.add_argument('problem', help='Problem ID')
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Target directory')
    parser.add_argument('--add', action='store_true', help='Add a new custom test case')
    parser.add_argument('--no-out', action='store_true', help='Skip generating expected output')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    problem = args.problem.replace('.cpp', '')
    directory = args.directory

    add_mode = args.add
    no_output = args.no_out

    if add_mode:
        add_test(problem, directory, with_output=not no_output)
        return

    source = os.path.join(directory, f"{problem}.cpp")
    if not os.path.exists(source):
        error(f"Error: {problem}.cpp not found.")
        sys.exit(1)

    config = load_config()
    binary = os.path.join(directory, f".{problem}")

    info("Compiling...")
    result = compile_from_config(source, binary, config)
    if not result.success:
        error("Compilation failed:")
        log(result.stderr)
        sys.exit(1)

    try:
        samples = find_samples(directory, problem)

        if samples and sys.stdin.isatty():
            info(f"Running {len(samples)} sample(s)...\n")
            success_result = run_with_samples(binary, samples)
            sys.exit(0 if success_result else 1)
        else:
            # Interactive mode or piped stdin
            if not sys.stdin.isatty():
                result = subprocess.run([binary], stdin=sys.stdin)
            else:
                info("Running interactively (Ctrl+D to end input)...")
                result = subprocess.run([binary])
            sys.exit(result.returncode)
    except subprocess.TimeoutExpired:
        error("Time limit exceeded (10s)")
        sys.exit(1)
    finally:
        if os.path.exists(binary):
            os.remove(binary)
