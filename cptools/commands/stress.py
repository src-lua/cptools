#!/usr/bin/env python3
"""
Usage: cptools stress <solution> <brute> <gen> [options]

Stress test: compare solution vs brute force with random inputs.

Options:
  --checker <chk>   Use custom checker (default: byte comparison)

Examples:
  cptools stress A A-brute gen
  cptools stress A A-brute gen --checker checker
"""
import os
import sys
import argparse
import signal
import subprocess

from cptools.lib.config import load_config
from cptools.lib import compile_from_config
from cptools.lib.io import error, success, warning, info, header, bold

TEMP_FILES = ['_stress_sol', '_stress_brt', '_stress_gen', '_stress_chk',
              '_stress_in', '_stress_out', '_stress_out2']

def cleanup():
    """Remove temporary files."""
    for f in TEMP_FILES:
        if os.path.exists(f):
            os.remove(f)

def get_parser():
    """Creates and returns the argparse parser for the stress command."""
    parser = argparse.ArgumentParser(description="Stress test: compare solution vs brute force with random inputs.")
    parser.add_argument('solution', help='Solution file')
    parser.add_argument('brute', help='Brute force file')
    parser.add_argument('gen', help='Generator file')
    parser.add_argument('--checker', help='Custom checker file')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    sol_name = args.solution.replace('.cpp', '')
    brute_name = args.brute.replace('.cpp', '')
    gen_name = args.gen.replace('.cpp', '')
    checker_name = args.checker.replace('.cpp', '') if args.checker else None

    # Register cleanup on exit
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(1)))
    signal.signal(signal.SIGTERM, lambda s, f: (cleanup(), sys.exit(1)))

    config = load_config()

    header("--- Stress Test ---")
    print(f"  Solution:  {sol_name}.cpp")
    print(f"  Brute:     {brute_name}.cpp")
    print(f"  Generator: {gen_name}.cpp")
    if checker_name:
        print(f"  Checker:   {checker_name}.cpp")
    print()

    # Compile all files
    info("Compiling...")

    sources = [
        (f"{sol_name}.cpp", "_stress_sol"),
        (f"{brute_name}.cpp", "_stress_brt"),
        (f"{gen_name}.cpp", "_stress_gen"),
    ]
    if checker_name:
        sources.append((f"{checker_name}.cpp", "_stress_chk"))

    for src, binary in sources:
        if not os.path.exists(src):
            error(f"Error: {src} not found.")
            cleanup()
            sys.exit(1)
        result = compile_from_config(src, binary, config)
        if not result.success:
            error(f"Compilation failed for {src}:")
            print(result.stderr)
            cleanup()
            sys.exit(1)

    success("All compiled.")
    print()
    info("Running stress test (Ctrl+C to stop)...")
    print()

    i = 0
    try:
        for i in range(1, 1_000_000):
            # Generate input
            with open('_stress_in', 'w') as f:
                gen_result = subprocess.run(
                    ['./_stress_gen', str(i)],
                    stdout=f, stderr=subprocess.DEVNULL,
                    timeout=10,
                )
            if gen_result.returncode != 0:
                error(f"Generator failed on iteration {i}")
                break

            # Run solution
            with open('_stress_in', 'r') as fin, open('_stress_out', 'w') as fout:
                sol_result = subprocess.run(
                    ['./_stress_sol'],
                    stdin=fin, stdout=fout, stderr=subprocess.DEVNULL,
                    timeout=10,
                )

            # Run brute force
            with open('_stress_in', 'r') as fin, open('_stress_out2', 'w') as fout:
                brute_result = subprocess.run(
                    ['./_stress_brt'],
                    stdin=fin, stdout=fout, stderr=subprocess.DEVNULL,
                    timeout=10,
                )

            # Check for runtime errors
            if sol_result.returncode != 0:
                error(f"Solution RE on iteration {i}")
                break
            if brute_result.returncode != 0:
                error(f"Brute force RE on iteration {i}")
                break

            # Compare outputs
            if checker_name:
                chk_result = subprocess.run(
                    ['./_stress_chk', '_stress_in', '_stress_out', '_stress_out2'],
                    capture_output=True, text=True,
                    timeout=10,
                )
                match = chk_result.returncode == 0
            else:
                with open('_stress_out', 'r') as f1, open('_stress_out2', 'r') as f2:
                    match = f1.read() == f2.read()

            if not match:
                error(f"Mismatch on iteration {i}!")
                print()

                with open('_stress_in', 'r') as f:
                    bold("Input:")
                    print(f.read())

                with open('_stress_out', 'r') as f:
                    bold("Solution output:")
                    print(f.read())

                with open('_stress_out2', 'r') as f:
                    bold("Brute output:")
                    print(f.read())

                break
            else:
                success(f"  #{i} OK", end='\r')

        else:
            print()
            success("1000000 iterations passed.")

    except subprocess.TimeoutExpired:
        print()
        error(f"Timeout on iteration {i}")
    except KeyboardInterrupt:
        print("\n")
        info(f"Stopped after {i} iterations.")
    finally:
        cleanup()
