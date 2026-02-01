#!/usr/bin/env python3
"""
Create a new contest with problem files.

Usage:
    cptools new <contest_url>
    cptools new  # interactive mode

Supports Codeforces, AtCoder, vJudge.
"""
import os
import sys

from .common import Colors, get_repo_root
from .config import load_config
from lib import (
    parse_contest_url,
    parse_problem_range,
    generate_header,
    create_problem_file,
    detect_judge
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = get_repo_root()
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "template.cpp")


def get_input(prompt, default=None):
    """Get user input with optional default value."""
    text = f"{Colors.BLUE}{prompt}{Colors.ENDC}"
    if default:
        text += f" [Default: {default}]"
    text += ": "
    value = input(text).strip()
    return value if value else default


def create_contest_from_url(url):
    """Create contest structure from URL."""
    config = load_config()
    contest_info = parse_contest_url(url)

    if not contest_info:
        print(f"{Colors.FAIL}Error: Could not parse contest URL.{Colors.ENDC}")
        print(f"  Supported: Codeforces, AtCoder, vJudge")
        sys.exit(1)

    if not os.path.exists(TEMPLATE_PATH):
        print(f"{Colors.FAIL}Error: template.cpp not found.{Colors.ENDC}")
        sys.exit(1)

    # Get contest name
    default_name = contest_info['contest_id']
    contest_name = get_input("Contest name", default_name)

    # Get problem range
    default_range = contest_info.get('default_range', 'A~E')
    problem_range_str = get_input("Problem range (e.g., A~E)", default_range)
    problems = parse_problem_range(problem_range_str)

    # Create directory structure
    dest_dir = os.path.join(ROOT_DIR, contest_info['platform'], contest_name)
    os.makedirs(dest_dir, exist_ok=True)

    print(f"\n{Colors.HEADER}--- Creating Contest ---{Colors.ENDC}")
    print(f"  Platform: {contest_info['platform']}")
    print(f"  Name: {contest_name}")
    print(f"  Problems: {', '.join(problems)}")
    print(f"  Directory: {dest_dir}\n")

    # Try to fetch problem names
    problem_names = {}
    judge = detect_judge(url)
    if judge:
        try:
            print(f"{Colors.BLUE}Fetching problem names...{Colors.ENDC}")
            problem_names = judge.fetch_contest_problems(contest_info['contest_id'])
            if problem_names:
                print(f"{Colors.GREEN}Found {len(problem_names)} problem name(s){Colors.ENDC}")
        except Exception:
            print(f"{Colors.WARNING}Could not fetch problem names (will use defaults){Colors.ENDC}")

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
        header = generate_header(
            problem_id=prob_char,
            link=link,
            problem_name=prob_name,
            author=config["author"]
        )

        # Create file
        filename = f"{prob_char}.cpp"
        filepath = os.path.join(dest_dir, filename)

        if os.path.exists(filepath):
            print(f"  {Colors.WARNING}! {filename} already exists{Colors.ENDC}")
            continue

        create_problem_file(filepath, TEMPLATE_PATH, header)
        print(f"  {Colors.GREEN}+ {filename}{Colors.ENDC}")
        created += 1

    print(f"\n{Colors.BOLD}Created {created}/{len(problems)} file(s) in {dest_dir}{Colors.ENDC}")

    # Update info.md
    try:
        from .update import generate_info_md
        generate_info_md(dest_dir)
        print(f"{Colors.BLUE}Generated info.md{Colors.ENDC}")
    except Exception:
        pass


def create_contest_interactive():
    """Create contest interactively."""
    print(f"{Colors.HEADER}--- Contest Setup ---{Colors.ENDC}")
    print("1. Codeforces (Contest)")
    print("2. Codeforces (Training/Group)")
    print("3. Codeforces (Gym)")
    print("4. AtCoder")
    print("5. vJudge")
    print("6. Other")

    choice = get_input("Choose platform", "1")

    if choice == "1":
        contest_id = get_input("Contest ID (e.g., 1234)")
        url = f"https://codeforces.com/contest/{contest_id}"
        create_contest_from_url(url)
    elif choice == "2":
        config = load_config()
        group_id = get_input("Group ID", config.get("default_group_id", ""))
        contest_id = get_input("Contest ID")
        url = f"https://codeforces.com/group/{group_id}/contest/{contest_id}"
        create_contest_from_url(url)
    elif choice == "3":
        contest_id = get_input("Gym ID")
        url = f"https://codeforces.com/gym/{contest_id}"
        create_contest_from_url(url)
    elif choice == "4":
        contest_id = get_input("Contest ID (e.g., abc300)")
        url = f"https://atcoder.jp/contests/{contest_id}"
        create_contest_from_url(url)
    elif choice == "5":
        contest_id = get_input("Contest ID")
        url = f"https://vjudge.net/contest/{contest_id}"
        create_contest_from_url(url)
    else:
        # Other - manual setup
        config = load_config()
        platform = get_input("Platform name", "Other")
        contest_name = get_input("Contest name")
        problem_range_str = get_input("Problem range (e.g., A~E)", "A~E")
        problems = parse_problem_range(problem_range_str)

        dest_dir = os.path.join(ROOT_DIR, platform, contest_name)
        os.makedirs(dest_dir, exist_ok=True)

        print(f"\n{Colors.HEADER}--- Creating Contest ---{Colors.ENDC}")
        print(f"  Platform: {platform}")
        print(f"  Name: {contest_name}")
        print(f"  Problems: {', '.join(problems)}\n")

        for prob_char in problems:
            header = generate_header(
                problem_id=prob_char,
                link="",
                problem_name=None,
                author=config["author"]
            )
            filename = f"{prob_char}.cpp"
            filepath = os.path.join(dest_dir, filename)
            create_problem_file(filepath, TEMPLATE_PATH, header)
            print(f"  {Colors.GREEN}+ {filename}{Colors.ENDC}")

        print(f"\n{Colors.BOLD}Created {len(problems)} file(s) in {dest_dir}{Colors.ENDC}")


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
        if url.startswith('http://') or url.startswith('https://'):
            create_contest_from_url(url)
        else:
            print(f"{Colors.FAIL}Error: Expected a URL or no arguments for interactive mode{Colors.ENDC}")
            print(f"  Usage: cptools new <url>")
            print(f"         cptools new  # interactive")
            sys.exit(1)
    else:
        create_contest_interactive()


if __name__ == "__main__":
    main()
