#!/usr/bin/env python3
import os
import sys
import re
from datetime import datetime
from pathlib import Path

from .common import Colors, get_repo_root, PLATFORM_DIRS

def get_status_emoji(status):
    """Map status to emoji."""
    status_lower = status.lower().strip()

    # Pending / Not attempted
    if status_lower in ['~', 'pending', 'not attempted', '']:
        return '⬜'

    # Solved/Accepted
    elif status_lower in ['solved', 'accepted', 'ac']:
        return '✅'

    # In Progress
    elif status_lower in ['attempting', 'in progress', 'wip']:
        return '🔄'

    # Wrong Answer
    elif status_lower in ['wa', 'wrong answer']:
        return '⚠️'

    # Time Limit Exceeded
    elif status_lower in ['tle', 'time limit', 'time limit exceeded']:
        return '⏱️'

    # Memory Limit Exceeded
    elif status_lower in ['mle', 'memory limit', 'memory limit exceeded']:
        return '💾'

    # Runtime Error
    elif status_lower in ['re', 'runtime error']:
        return '💥'

    # Not solved / Unsolved
    else:
        return '❌'

def read_problem_info(filepath):
    """Extract problem information from C++ file header."""
    try:
        with open(filepath, 'r') as f:
            content = f.read(500)  # Read first 500 chars (header should be there)

        info = {
            'problem': None,
            'link': None,
            'status': '~',
            'created': None
        }

        for line in content.split('\n'):
            if 'Problem:' in line:
                info['problem'] = line.split('Problem:')[1].strip().replace('*/', '').strip()
            elif 'Link:' in line:
                info['link'] = line.split('Link:')[1].strip().replace('*/', '').strip()
            elif 'Status:' in line:
                info['status'] = line.split('Status:')[1].strip().replace('*/', '').strip()
            elif 'Created:' in line:
                info['created'] = line.split('Created:')[1].strip().replace('*/', '').strip()

        return info
    except Exception as e:
        print(f"{Colors.WARNING}Could not read {filepath}: {e}{Colors.ENDC}")
        return None

def detect_platform_from_path(path):
    """Detect contest platform from directory structure."""
    parts = Path(path).parts

    platform_map = {
        'Trainings': 'Trainings',
        'Codeforces': 'Codeforces',
        'vJudge': 'vJudge',
        'AtCoder': 'AtCoder',
        'Yosupo': 'Yosupo',
        'Other': 'Other',
    }

    # Check for Codeforces/Gym (nested platform dir)
    if 'Codeforces' in parts:
        idx = parts.index('Codeforces')
        if idx + 1 < len(parts) and parts[idx + 1] == 'Gym':
            if idx + 2 < len(parts):
                return 'Codeforces Gym', parts[idx + 2]
            return 'Codeforces Gym', Path(path).name

    # Other/ uses the subfolder name as the display name
    if 'Other' in parts:
        idx = parts.index('Other')
        if idx + 1 < len(parts):
            name = parts[idx + 1]
            return name, name

    for key, label in platform_map.items():
        if key in parts:
            idx = parts.index(key)
            if idx + 1 < len(parts):
                return label, parts[idx + 1]

    return 'Contest', Path(path).name

def generate_info_md(directory):
    """Generate or update info.md for the contest directory."""
    directory = os.path.abspath(directory)

    # Find all .cpp files
    cpp_files = sorted([f for f in os.listdir(directory) if f.endswith('.cpp')])

    if not cpp_files:
        print(f"{Colors.WARNING}No .cpp files found in {directory}{Colors.ENDC}")
        return

    print(f"{Colors.BLUE}Reading {len(cpp_files)} problem files...{Colors.ENDC}")

    # Extract problem information
    problems = []
    for cpp_file in cpp_files:
        filepath = os.path.join(directory, cpp_file)
        info = read_problem_info(filepath)

        if info:
            char = cpp_file.replace('.cpp', '')
            problems.append({
                'char': char,
                'file': cpp_file,
                **info
            })

    if not problems:
        print(f"{Colors.FAIL}No valid problem headers found.{Colors.ENDC}")
        return

    # Detect platform and contest
    platform, contest_id = detect_platform_from_path(directory)

    # Generate markdown content
    content = f"# {platform}"
    if contest_id != Path(directory).name:
        content += f" - {contest_id}"
    content += "\n\n"

    # Add contest link if available (extract from first problem link)
    if problems[0]['link']:
        first_link = problems[0]['link']
        if 'codeforces.com/group' in first_link:
            match = re.search(r'codeforces\.com/group/([^/]+)/contest/(\d+)', first_link)
            if match:
                content += f"**Contest**: [Codeforces Group]({first_link.rsplit('/problem/', 1)[0]})\n\n"
        elif 'codeforces.com/contest' in first_link:
            contest_url = first_link.rsplit('/problem/', 1)[0]
            content += f"**Contest**: [Codeforces]({contest_url})\n\n"
        elif 'vjudge.net' in first_link:
            contest_url = first_link.rsplit('#problem/', 1)[0]
            content += f"**Contest**: [vJudge]({contest_url})\n\n"
        elif 'atcoder.jp' in first_link:
            match = re.search(r'atcoder\.jp/contests/([^/]+)', first_link)
            if match:
                content += f"**Contest**: [AtCoder](https://atcoder.jp/contests/{match.group(1)})\n\n"
        elif 'judge.yosupo.jp' in first_link:
            content += f"**Judge**: [Yosupo Library Checker](https://judge.yosupo.jp)\n\n"

    # Add created date (from first problem or current time)
    created = problems[0]['created'] if problems[0]['created'] else datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    content += f"**Created**: {created}\n\n"

    # Statistics
    solved_count = sum(1 for p in problems if p['status'].lower() in ['solved', 'accepted', 'ac'])
    content += f"**Progress**: {solved_count}/{len(problems)} solved\n\n"

    # Problems table
    content += "## Problems\n\n"
    content += "| Problem | Status |\n"
    content += "|---------|--------|\n"

    for p in problems:
        # Get emoji for status
        emoji = get_status_emoji(p['status'])

        # Format problem title
        problem_title = p['problem'] if p['problem'] else p['char']

        # Format status label
        status_label = '' if p['status'] in ['~', ''] else p['status']

        # Add link if available
        if p['link']:
            content += f"| [{problem_title}]({p['link']}) | {emoji} {status_label} |\n"
        else:
            content += f"| {problem_title} | {emoji} {status_label} |\n"

    # Write info.md
    info_path = os.path.join(directory, "info.md")
    with open(info_path, 'w') as f:
        f.write(content)

    print(f"{Colors.GREEN}✓ Generated {info_path}{Colors.ENDC}")
    print(f"{Colors.GREEN}✓ Progress: {solved_count}/{len(problems)} solved{Colors.ENDC}")

ROOT_DIR = get_repo_root()

def update_all():
    """Recursively update info.md for all contest directories in the repo."""
    updated = 0
    for platform_dir in PLATFORM_DIRS:
        platform_path = os.path.join(ROOT_DIR, platform_dir)
        if not os.path.isdir(platform_path):
            continue

        for root, dirs, files in os.walk(platform_path):
            cpp_files = [f for f in files if f.endswith('.cpp')]
            if cpp_files:
                print(f"\n{Colors.BLUE}> {os.path.relpath(root, ROOT_DIR)}{Colors.ENDC}")
                generate_info_md(root)
                updated += 1

    if updated == 0:
        print(f"{Colors.WARNING}No contest directories found.{Colors.ENDC}")
    else:
        print(f"\n{Colors.BOLD}Updated {updated} contest(s).{Colors.ENDC}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        print(f"{Colors.HEADER}--- Updating All Contest Info ---{Colors.ENDC}")
        update_all()
        return

    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.getcwd()

    if not os.path.isdir(directory):
        print(f"{Colors.FAIL}Error: {directory} is not a valid directory.{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.HEADER}--- Updating Contest Info ---{Colors.ENDC}")
    print(f"Directory: {directory}\n")

    generate_info_md(directory)

if __name__ == "__main__":
    main()
