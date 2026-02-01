#!/usr/bin/env python3
"""
Bundle a solution by expanding local #include "..." directives into a single file.

Usage:
    cptools bundle <problem>           Bundle and copy to clipboard
    cptools bundle <problem> -o FILE   Bundle and write to file
    cptools bundle <problem> -i        Bundle in-place (overwrites source)
"""
import os
import sys
import re
import subprocess

from .common import Colors
from .config import load_config


def get_include_paths(config):
    """Extract -I paths from compiler_flags."""
    paths = []
    for flag in config.get("compiler_flags", []):
        if flag.startswith("-I"):
            paths.append(os.path.expanduser(flag[2:]))
    return paths


def resolve_include(include_path, current_dir, include_dirs):
    """Resolve a quoted include path. Try relative to current file first, then -I dirs."""
    candidate = os.path.normpath(os.path.join(current_dir, include_path))
    if os.path.isfile(candidate):
        return candidate

    for inc_dir in include_dirs:
        candidate = os.path.normpath(os.path.join(inc_dir, include_path))
        if os.path.isfile(candidate):
            return candidate

    return None


def bundle_file(filepath, include_dirs, included_files, seen_sys_includes, seen_using, is_root=False):
    """Recursively expand local includes, deduplicating system includes and using-directives."""
    filepath = os.path.normpath(os.path.realpath(filepath))

    if filepath in included_files:
        return []
    included_files.add(filepath)

    current_dir = os.path.dirname(filepath)

    with open(filepath, 'r') as f:
        lines = f.readlines()

    result = []
    in_block_comment = False

    for line in lines:
        stripped = line.strip()

        # Skip block comments in library files
        if not is_root:
            if in_block_comment:
                if '*/' in stripped:
                    in_block_comment = False
                continue
            if stripped.startswith('/*'):
                if '*/' not in stripped:
                    in_block_comment = True
                continue

        if stripped == '#pragma once':
            continue

        if re.match(r'#include\s*<.+?>', stripped):
            if stripped in seen_sys_includes:
                continue
            seen_sys_includes.add(stripped)
            result.append(line)
            continue

        if stripped == 'using namespace std;':
            if seen_using[0]:
                continue
            seen_using[0] = True
            result.append(line)
            continue

        local_match = re.match(r'#include\s*"(.+?)"', stripped)
        if local_match:
            include_path = local_match.group(1)
            if 'debug' in include_path.lower():
                result.append(line)
                continue
            resolved = resolve_include(include_path, current_dir, include_dirs)
            if resolved:
                expanded = bundle_file(resolved, include_dirs, included_files, seen_sys_includes, seen_using)
                while expanded and expanded[-1].strip() == '':
                    expanded.pop()
                while expanded and expanded[0].strip() == '':
                    expanded.pop(0)
                result.extend(expanded)
                result.append('\n')
            else:
                result.append(line)
            continue

        result.append(line)

    return result


def copy_to_clipboard(text):
    """Try to copy text to clipboard. Returns True on success."""
    for cmd in [['xclip', '-selection', 'clipboard'], ['xsel', '--clipboard', '--input'], ['wl-copy']]:
        try:
            proc = subprocess.run(cmd, input=text, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if proc.returncode == 0:
                return True
        except FileNotFoundError:
            continue
    return False


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print(__doc__.strip())
        sys.exit(0)

    problem = sys.argv[1].replace('.cpp', '')

    inplace = '-i' in sys.argv

    output_file = None
    if '-o' in sys.argv:
        idx = sys.argv.index('-o')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
        else:
            print(f"{Colors.FAIL}Error: -o requires a filename.{Colors.ENDC}", file=sys.stderr)
            sys.exit(1)

    source = os.path.join(os.getcwd(), f"{problem}.cpp")

    if not os.path.exists(source):
        print(f"{Colors.FAIL}Error: {problem}.cpp not found.{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)

    config = load_config()
    include_dirs = get_include_paths(config)

    output = ''.join(bundle_file(source, include_dirs, set(), set(), [False], is_root=True))
    output = re.sub(r'\n{3,}', '\n\n', output)

    if inplace:
        with open(source, 'w') as f:
            f.write(output)
        print(f"{Colors.GREEN}Bundled in-place: {problem}.cpp{Colors.ENDC}", file=sys.stderr)
    elif output_file:
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"{Colors.GREEN}Bundled to {output_file}{Colors.ENDC}", file=sys.stderr)
    else:
        if copy_to_clipboard(output):
            print(f"{Colors.GREEN}Bundled and copied to clipboard!{Colors.ENDC}", file=sys.stderr)
        else:
            print(output)  # Bundled code goes to stdout for redirection
            print(f"\n{Colors.WARNING}Could not copy to clipboard (install xclip or xsel).{Colors.ENDC}",
                  file=sys.stderr)


if __name__ == "__main__":
    main()
