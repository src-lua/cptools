#!/usr/bin/env python3
"""
Usage: cptools test <problem> [directory] [options]

Compile and test a solution against samples or custom inputs.

Options:
  --add              Add a new custom test case
  --no-out           Skip generating expected output (when adding test)
  -i, --interactive  Force interactive mode even if samples exist

Examples:
  cptools test A
  cptools test A --add
  cptools test A --add --no-out
  cptools test A --interactive
"""
import os
import sys
import argparse
import subprocess
import time
import threading

from lib.config import load_config
from lib import find_samples, compile_from_config, next_test_index
from lib.io import log, error, success, info, header, bold

def get_process_memory(pid):
    """Get current memory stats from /proc/[pid]/status."""
    try:
        with open(f'/proc/{pid}/status', 'r') as f:
            vm_peak = 0
            vm_size = 0
            vm_rss = 0

            for line in f:
                if line.startswith('VmPeak:'):
                    vm_peak = int(line.split()[1])
                elif line.startswith('VmSize:'):
                    vm_size = int(line.split()[1])
                elif line.startswith('VmRSS:'):
                    vm_rss = int(line.split()[1])

            return max(vm_peak, vm_size), vm_rss
    except:
        return 0, 0

def monitor_memory(pid, memory_stats):
    """Monitor process memory usage via /proc/[pid]/status.

    Uses aggressive sampling at start, then periodic checks.
    """
    max_vm_size = 0
    max_rss = 0

    # Phase 1: Aggressive sampling (no sleep) for first 1000 reads
    # This catches memory allocated at process start
    for _ in range(1000):
        vm, rss = get_process_memory(pid)
        if vm == 0 and rss == 0:
            break  # Process ended
        max_vm_size = max(max_vm_size, vm)
        max_rss = max(max_rss, rss)

    # Phase 2: Periodic sampling with tiny sleep
    for _ in range(10000):
        vm, rss = get_process_memory(pid)
        if vm == 0 and rss == 0:
            break  # Process ended
        max_vm_size = max(max_vm_size, vm)
        max_rss = max(max_rss, rss)
        time.sleep(0.0001)  # 0.1ms

    memory_stats['vm_peak'] = max_vm_size
    memory_stats['rss_peak'] = max_rss

def run_with_samples(binary, samples):
    """Run binary against sample test cases."""
    passed = 0
    total = len(samples)

    for sample in samples:
        with open(sample['in'], 'r') as f:
            input_data = f.read()

        # Start process and monitor memory
        start_time = time.time()

        process = subprocess.Popen(
            [binary],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Start memory monitoring thread
        memory_stats = {'vm_peak': 0, 'rss_peak': 0}
        monitor_thread = threading.Thread(target=monitor_memory, args=(process.pid, memory_stats))
        monitor_thread.daemon = True
        monitor_thread.start()

        # Run process with timeout
        try:
            stdout, stderr = process.communicate(input=input_data, timeout=10)
            elapsed_time = time.time() - start_time
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            monitor_thread.join(timeout=0.1)
            raise

        # Wait for monitor thread to finish
        monitor_thread.join(timeout=0.1)

        actual = stdout.rstrip('\n')
        time_seconds = elapsed_time

        # Get memory stats
        vm_peak_kb = memory_stats.get('vm_peak', 0)
        rss_peak_kb = memory_stats.get('rss_peak', 0)

        # Format time and memory strings
        if time_seconds < 1:
            time_str = f"{time_seconds*1000:.0f}ms"
        else:
            time_str = f"{time_seconds:.2f}s"

        # Format memory: "RSS (real) / VM (virtual)"
        if vm_peak_kb > 0 and rss_peak_kb > 0:
            if vm_peak_kb < 1024:
                vm_str = f"{vm_peak_kb}KB"
            else:
                vm_str = f"{vm_peak_kb/1024:.1f}MB"

            if rss_peak_kb < 1024:
                rss_str = f"{rss_peak_kb}KB"
            else:
                rss_str = f"{rss_peak_kb/1024:.1f}MB"

            mem_str = f"{rss_str} / {vm_str}"
        else:
            mem_str = None

        if sample['out']:
            with open(sample['out'], 'r') as f:
                expected = f.read().rstrip('\n')

            if actual == expected:
                stats = f"{time_str}, {mem_str}" if mem_str else time_str
                success(f"  Sample {sample['num']}: PASS ({stats})")
                passed += 1
            else:
                stats = f"{time_str}, {mem_str}" if mem_str else time_str
                error(f"  Sample {sample['num']}: FAIL ({stats})")
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
            stats = f"{time_str}, {mem_str}" if mem_str else time_str
            info(f"  Sample {sample['num']}: (no expected output) ({stats})")
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
    parser.add_argument('-i', '--interactive', action='store_true', help='Force interactive mode even if samples exist')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    problem = args.problem.replace('.cpp', '')
    directory = args.directory

    add_mode = args.add
    no_output = args.no_out
    force_interactive = args.interactive

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

        # If --interactive flag is set, ignore samples and run interactively
        if force_interactive:
            if not sys.stdin.isatty():
                result = subprocess.run([binary], stdin=sys.stdin)
            else:
                info("Running interactively (Ctrl+D to end input)...")
                result = subprocess.run([binary])
            sys.exit(result.returncode)

        # If samples exist, use them (unless --interactive was specified)
        if samples:
            info(f"Running {len(samples)} sample(s)...\n")
            success_result = run_with_samples(binary, samples)
            sys.exit(0 if success_result else 1)
        else:
            # No samples: interactive mode or piped stdin
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
