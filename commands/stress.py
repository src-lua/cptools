#!/usr/bin/env python3
"""
Stress test: compare solution vs brute force with random inputs.

Usage:
    cptools stress <solution> <brute> <gen> [--checker <checker>]

Examples:
    cptools stress A A-brute gen
    cptools stress A A-brute gen --checker checker

Arguments are filenames without .cpp extension.
The generator receives the iteration number as argument (./gen 1, ./gen 2, ...).
Without --checker, outputs are compared byte-by-byte.
With --checker, runs: ./checker input output_sol output_brute
"""
import os
import sys
import signal
import subprocess

from .common import Colors
from .config import load_config

TEMP_FILES = ['_stress_sol', '_stress_brt', '_stress_gen', '_stress_chk',
              '_stress_in', '_stress_out', '_stress_out2']

def cleanup():
    """Remove temporary files."""
    for f in TEMP_FILES:
        if os.path.exists(f):
            os.remove(f)

def compile_file(source_cpp, binary, config):
    """Compile a C++ file. Returns True on success."""
    compiler = config["compiler"]
    flags = config["compiler_flags"]
    cmd = [compiler] + flags + [source_cpp, "-o", binary]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"{Colors.FAIL}Compilation failed for {source_cpp}:{Colors.ENDC}")
        print(result.stderr)
        return False
    return True

def main():
    if len(sys.argv) < 4:
        print(f"{Colors.FAIL}Usage: cptools stress <solution> <brute> <gen> [--checker <checker>]{Colors.ENDC}")
        print(f"  Example: cptools stress A A-brute gen")
        print(f"  Example: cptools stress A A-brute gen --checker checker")
        sys.exit(1)

    sol_name = sys.argv[1].replace('.cpp', '')
    brute_name = sys.argv[2].replace('.cpp', '')
    gen_name = sys.argv[3].replace('.cpp', '')

    checker_name = None
    if '--checker' in sys.argv:
        idx = sys.argv.index('--checker')
        if idx + 1 < len(sys.argv):
            checker_name = sys.argv[idx + 1].replace('.cpp', '')
        else:
            print(f"{Colors.FAIL}Error: --checker requires an argument.{Colors.ENDC}")
            sys.exit(1)

    # Register cleanup on exit
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(1)))
    signal.signal(signal.SIGTERM, lambda s, f: (cleanup(), sys.exit(1)))

    config = load_config()

    print(f"{Colors.HEADER}--- Stress Test ---{Colors.ENDC}")
    print(f"  Solution:  {sol_name}.cpp")
    print(f"  Brute:     {brute_name}.cpp")
    print(f"  Generator: {gen_name}.cpp")
    if checker_name:
        print(f"  Checker:   {checker_name}.cpp")
    print()

    # Compile all files
    print(f"{Colors.BLUE}Compiling...{Colors.ENDC}")

    sources = [
        (f"{sol_name}.cpp", "_stress_sol"),
        (f"{brute_name}.cpp", "_stress_brt"),
        (f"{gen_name}.cpp", "_stress_gen"),
    ]
    if checker_name:
        sources.append((f"{checker_name}.cpp", "_stress_chk"))

    for src, binary in sources:
        if not os.path.exists(src):
            print(f"{Colors.FAIL}Error: {src} not found.{Colors.ENDC}")
            cleanup()
            sys.exit(1)
        if not compile_file(src, binary, config):
            cleanup()
            sys.exit(1)

    print(f"{Colors.GREEN}All compiled.{Colors.ENDC}\n")
    print(f"{Colors.BLUE}Running stress test (Ctrl+C to stop)...{Colors.ENDC}\n")

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
                print(f"{Colors.FAIL}Generator failed on iteration {i}{Colors.ENDC}")
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
                print(f"{Colors.FAIL}Solution RE on iteration {i}{Colors.ENDC}")
                break
            if brute_result.returncode != 0:
                print(f"{Colors.FAIL}Brute force RE on iteration {i}{Colors.ENDC}")
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
                print(f"{Colors.FAIL}Mismatch on iteration {i}!{Colors.ENDC}\n")

                with open('_stress_in', 'r') as f:
                    print(f"{Colors.BOLD}Input:{Colors.ENDC}")
                    print(f.read())

                with open('_stress_out', 'r') as f:
                    print(f"{Colors.BOLD}Solution output:{Colors.ENDC}")
                    print(f.read())

                with open('_stress_out2', 'r') as f:
                    print(f"{Colors.BOLD}Brute output:{Colors.ENDC}")
                    print(f.read())

                break
            else:
                print(f"  {Colors.GREEN}#{i} OK{Colors.ENDC}", end='\r')

        else:
            print(f"\n{Colors.GREEN}1000000 iterations passed.{Colors.ENDC}")

    except subprocess.TimeoutExpired:
        print(f"\n{Colors.FAIL}Timeout on iteration {i}{Colors.ENDC}")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BLUE}Stopped after {i} iterations.{Colors.ENDC}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
