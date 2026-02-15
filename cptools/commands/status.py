#!/usr/bin/env python3
"""
Usage: cptools status [directory]

Show a quick summary of the current contest directory.

Arguments:
  directory     Target directory (default: current)

Examples:
  cptools status
  cptools status /path/to/contest
"""
import os
import sys
import argparse
import shutil
from cptools.lib.display_utils import get_status_emoji
from cptools.lib.fileops import read_problem_header, generate_header
from cptools.lib.io import error, warning, Colors, log, info
from cptools.lib.config import load_config

def get_parser():
    parser = argparse.ArgumentParser(description="Show a quick summary of the current contest directory.")
    parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Target directory (default: current)')
    parser.add_argument('--grid', action='store_true', dest='force_compact',
                       help='Force grid display mode')
    parser.add_argument('--wide', action='store_true',
                       help='Force wide display mode')
    return parser

def get_emoji_display_width(emoji):
    """Get emoji display width (1 or 2). Uses wcwidth > manual > fallback."""
    EMOJI_WIDTHS_MANUAL = {'⬜': 2, '⏱️': 1, '⚠️': 1}

    try:
        import wcwidth
        width = wcwidth.wcswidth(emoji)
        if width > 0:
            return min(width, 2)
    except (ImportError, TypeError):
        pass

    base = emoji[0] if emoji else ''
    if emoji in EMOJI_WIDTHS_MANUAL:
        return EMOJI_WIDTHS_MANUAL[emoji]
    if base in EMOJI_WIDTHS_MANUAL:
        return EMOJI_WIDTHS_MANUAL[base]

    if emoji:
        codepoint = ord(emoji[0])
        if 0x1F000 <= codepoint <= 0x1FFFF:
            return 2
        if codepoint in [0x2705, 0x274C, 0x274E, 0x2757]:
            return 2
        if 0x2600 <= codepoint <= 0x26FF:
            return 2
        if 0x2B00 <= codepoint <= 0x2BFF:
            return 1

    return 2

def get_display_mode(args, terminal_width):
    """Determine display mode based on flags or terminal width."""
    if args.force_compact:
        return 'grid'
    if args.wide:
        return 'normal'
    return 'grid' if terminal_width < 50 else 'normal'

def calculate_grid_columns(terminal_width):
    """Calculate number of columns for grid mode (1-4)."""
    cell_width = 8
    spacing = 2
    available_width = terminal_width - 2
    columns = max(1, available_width // (cell_width + spacing))
    return min(columns, 4)

def display_problems(problems, display_mode, terminal_width):
    """Display problems in grid or normal mode."""
    if display_mode == 'grid':
        columns = calculate_grid_columns(terminal_width)
        for i in range(0, len(problems), columns):
            row = problems[i:i+columns]
            cells = []
            for char, emoji, status, name in row:
                w = get_emoji_display_width(emoji)
                pad = " " * (3 - w)
                cells.append(f"{emoji}{pad}{Colors.BOLD}{char:<3}{Colors.ENDC}")
            log("  " + "   ".join(cells))
    else:
        for char, emoji, status, name in problems:
            w = get_emoji_display_width(emoji)
            pad_emoji = " " * (3 - w)
            st_str = status if status not in ['~', ''] else ""
            log(f"  {emoji}{pad_emoji}   {st_str:<4}    {Colors.BOLD}{char:<4}{Colors.ENDC} {name}")

def add_header_to_file(filepath, problem_id):
    """Add a header to a file that doesn't have one."""
    config = load_config()
    author = config.get('author', 'Unknown')

    with open(filepath, 'r') as f:
        content = f.read()

    header = generate_header(
        problem_id=problem_id,
        link='',
        problem_name=None,
        author=author,
        status='~'
    )

    with open(filepath, 'w') as f:
        f.write(header)
        f.write(content)


def run():
    parser = get_parser()
    args = parser.parse_args()

    try:
        terminal_size = shutil.get_terminal_size()
        terminal_width = terminal_size.columns
    except (AttributeError, ValueError):
        terminal_width = 80

    display_mode = get_display_mode(args, terminal_width)
    directory = args.directory

    if not os.path.isdir(directory):
        error(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    cpp_files = sorted([f for f in os.listdir(directory) if f.endswith('.cpp')])
    if not cpp_files:
        warning("No .cpp files found.")
        sys.exit(1)

    files_without_headers = []
    for cpp_file in cpp_files:
        filepath = os.path.join(directory, cpp_file)
        header = read_problem_header(filepath)
        if not header or header.problem is None:
            files_without_headers.append(cpp_file)

    if files_without_headers:
        warning(f"Found {len(files_without_headers)} file(s) without cptools headers:")
        for f in files_without_headers:
            info(f"  • {f}")
        response = input("\nAdd headers to these files? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            for cpp_file in files_without_headers:
                filepath = os.path.join(directory, cpp_file)
                problem_id = cpp_file.replace('.cpp', '')
                problem_display = problem_id.replace('_', ' ')
                add_header_to_file(filepath, problem_display)
                info(f"  ✓ Added header to {cpp_file}")
            print()

    counts = {}
    problems = []
    for cpp_file in cpp_files:
        filepath = os.path.join(directory, cpp_file)
        header = read_problem_header(filepath)
        if not header or header.problem is None:
            continue

        status = header.status.upper().strip()
        if status in ['~', '']:
            status = '~'
        counts[status] = counts.get(status, 0) + 1

        char = cpp_file.replace('.cpp', '')
        emoji = get_status_emoji(header.status)
        name = header.problem if header.problem else char
        problems.append((char, emoji, header.status, name))

    total = len(problems)
    ac = counts.get('AC', 0) + counts.get('SOLVED', 0) + counts.get('ACCEPTED', 0)

    dirname = os.path.basename(os.path.abspath(directory))
    log(f"{Colors.BOLD}{dirname}{Colors.ENDC}  {ac}/{total} solved\n")

    display_problems(problems, display_mode, terminal_width)

    log()
    parts = []
    if ac > 0:
        parts.append(f"{Colors.GREEN}{ac} AC{Colors.ENDC}")
    for key in ['WA', 'TLE', 'MLE', 'RE', 'WIP']:
        if counts.get(key, 0) > 0:
            parts.append(f"{Colors.WARNING}{counts[key]} {key}{Colors.ENDC}")
    pending = counts.get('~', 0)
    if pending > 0:
        parts.append(f"{pending} pending")
    log("  " + "  ".join(parts))
