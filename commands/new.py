#!/usr/bin/env python3
"""
Usage: cptools new [url]

Create a new contest with problem files from a URL or interactively.

Arguments:
  url           Contest URL (Codeforces, AtCoder, vJudge)

Examples:
  cptools new https://codeforces.com/contest/1234
  cptools new   # Interactive mode
"""
import os
import sys
import argparse
from datetime import date

from lib.fileops import get_repo_root
from lib.config import load_config
from lib import (
    parse_contest_url,
    parse_problem_range,
    generate_header,
    create_problem_file,
    detect_judge
)
from lib.io import error, success, warning, info, header, bold, Colors
from lib.judges import ALL_JUDGES

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = get_repo_root()
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "lib", "templates", "template.cpp")


def get_input(prompt, default=None):
    """Get user input with optional default value."""
    if default:
        prompt += f" [Default: {default}]"
    prompt += ": "
    # Use Colors directly in the input prompt
    value = input(f"{Colors.BLUE}{prompt}{Colors.ENDC}").strip()
    return value if value else default


def create_contest_from_url(url):
    """Create contest structure from URL."""
    config = load_config()
    contest_info = parse_contest_url(url)

    if not contest_info:
        error("Error: Could not parse contest URL.")
        print(f"  Supported: Codeforces, AtCoder, vJudge")
        sys.exit(1)

    if not os.path.exists(TEMPLATE_PATH):
        error("Error: template.cpp not found.")
        sys.exit(1)

    # Get contest name - use today's date for trainings
    if contest_info.get('is_training'):
        default_name = date.today().strftime('%Y-%m-%d')
    else:
        default_name = contest_info['contest_id']
    contest_name = get_input("Contest name", default_name)

    # Try to fetch problem names first
    problem_names = {}
    judge = detect_judge(url)
    if judge:
        try:
            info("Fetching problems from API...")
            problem_names = judge.fetch_contest_problems(contest_info['contest_id'])
            if problem_names:
                success(f"Found {len(problem_names)} problem(s)")
        except Exception:
            pass

    # Get problem range - use fetched problems if available
    if problem_names:
        problems = list(problem_names.keys())
        info(f"Auto-detected problems: {', '.join(problems)}")
    else:
        default_range = contest_info.get('default_range', 'A~E')
        problem_range_str = get_input("Problem range (e.g., A~E)", default_range)
        problems = parse_problem_range(problem_range_str)

    # Create directory structure
    dest_dir = os.path.join(ROOT_DIR, contest_info['platform'], contest_name)
    os.makedirs(dest_dir, exist_ok=True)

    print()
    header("--- Creating Contest ---")
    print(f"  Platform: {contest_info['platform']}")
    print(f"  Name: {contest_name}")
    print(f"  Problems: {', '.join(problems)}")
    print(f"  Directory: {dest_dir}\n")

    # Create problem files
    created = 0
    for prob_char in problems:
        # Generate problem URL
        base_url = contest_info['base_url']
        if contest_info.get('is_training'):
            link = base_url.format(
                group_id=contest_info.get('group_id'),
                id=contest_info['contest_id'],
                char=prob_char
            )
        else:
            link = base_url.format(id=contest_info['contest_id'], char=prob_char)

        # Get problem name if available
        prob_name = problem_names.get(prob_char)

        # Generate header
        problem_header = generate_header(
            problem_id=prob_char,
            link=link,
            problem_name=prob_name,
            author=config["author"]
        )

        # Create file
        filename = f"{prob_char}.cpp"
        filepath = os.path.join(dest_dir, filename)

        if os.path.exists(filepath):
            warning(f"  ! {filename} already exists")
            continue

        create_problem_file(filepath, TEMPLATE_PATH, problem_header)
        success(f"  + {filename}")
        created += 1

    print()
    bold(f"Created {created}/{len(problems)} file(s) in {dest_dir}")

    # Update info.md
    try:
        from .update import generate_info_md
        generate_info_md(dest_dir)
        info("Generated info.md")
    except Exception:
        pass


def create_contest_interactive():
    """Create contest interactively."""
    header("--- Interactive Contest Setup ---")

    # Generate menu dynamically from the list of available judges
    for i, judge in enumerate(ALL_JUDGES, 1):
        print(f"{i}. {judge.platform_name}")
    print(f"{len(ALL_JUDGES) + 1}. Other (Manual Setup)")
    print()

    try:
        choice_str = get_input("Choose platform", "1")
        choice = int(choice_str)
        if not (1 <= choice <= len(ALL_JUDGES) + 1):
            raise ValueError
    except (ValueError, TypeError):
        error("Invalid choice.")
        sys.exit(1)

    if choice <= len(ALL_JUDGES):
        selected_judge = ALL_JUDGES[choice - 1]
        # This simplified flow assumes a single ID is enough.
        # For complex URLs (like CF Groups), the user can pass the full URL directly.
        contest_id = get_input(f"Enter {selected_judge.platform_name} Contest ID")
        if not contest_id:
            error("Contest ID cannot be empty.")
            sys.exit(1)
        
        # Manually construct URL based on platform name.
        platform_name = selected_judge.platform_name
        url = None
        if platform_name == 'Codeforces':
            url = f"https://codeforces.com/contest/{contest_id}"
        elif platform_name == 'AtCoder':
            url = f"https://atcoder.jp/contests/{contest_id}"
        elif platform_name == 'vJudge':
            url = f"https://vjudge.net/contest/{contest_id}"

        if url:
            create_contest_from_url(url)
        else:
            error(f"Interactive contest creation for '{platform_name}' is not supported. Please provide the full URL.")
            sys.exit(1)
    else: # "Other" was chosen
        # Other - manual setup
        config = load_config()
        platform = get_input("Platform name", "Other")
        contest_name = get_input("Contest name")
        if not contest_name:
            error("Contest name cannot be empty.")
            sys.exit(1)
        problem_range_str = get_input("Problem range (e.g., A~E)", "A~E")
        problems = parse_problem_range(problem_range_str)
        dest_dir = os.path.join(ROOT_DIR, platform, contest_name)
        os.makedirs(dest_dir, exist_ok=True)

        print()
        header("--- Creating Contest ---")
        print(f"  Platform: {platform}")
        print(f"  Name: {contest_name}")
        print(f"  Problems: {', '.join(problems)}\n")

        for prob_char in problems:
            prob_header = generate_header(
                problem_id=prob_char,
                link="",
                problem_name=None,
                author=config["author"]
            )
            filename = f"{prob_char}.cpp"
            filepath = os.path.join(dest_dir, filename)
            create_problem_file(filepath, TEMPLATE_PATH, prob_header)
            success(f"  + {filename}")

        print()
        bold(f"Created {len(problems)} file(s) in {dest_dir}")


def get_parser():
    """Creates and returns the argparse parser for the new command."""
    parser = argparse.ArgumentParser(description="Create a new contest with problem files from a URL or interactively.")
    parser.add_argument('url', nargs='?', help='Contest URL (Codeforces, AtCoder, vJudge)')
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    if args.url:
        create_contest_from_url(args.url)
    else:
        create_contest_interactive()