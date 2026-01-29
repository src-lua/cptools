#!/usr/bin/env python3
import os
import sys
import re
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

from colors import Colors, get_repo_root

AUTHOR_NAME = "Lua"
DEFAULT_GROUP_ID = "yc7Yxny414"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = get_repo_root()
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "template.cpp")

def get_input(prompt, default=None):
    text = f"{Colors.BLUE}{prompt}{Colors.ENDC}"
    if default:
        text += f" [Default: {default}]"
    text += ": "
    value = input(text).strip()
    return value if value else default

def parse_contest_url(url):
    url = url.strip()

    # Extract problem letter from URL if present
    problem_match = re.search(r'(?:problem/|tasks/[^/]+_)([A-Za-z])', url)
    default_range = None
    if problem_match:
        problem_char = problem_match.group(1).upper()
        default_range = f"A~{problem_char}"

    cf_group_pattern = r'codeforces\.com/group/([^/]+)/contest/(\d+)'
    cf_contest_pattern = r'codeforces\.com/contest/(\d+)'
    cf_gym_pattern = r'codeforces\.com/gym/(\d+)'
    vjudge_pattern = r'vjudge\.net/contest/(\d+)'
    atcoder_pattern = r'atcoder\.jp/contests/([^/]+)'

    match = re.search(cf_group_pattern, url)
    if match:
        return {
            'platform': 'training',
            'base_url': 'https://codeforces.com/group/{group_id}/contest/{id}/problem/{char}',
            'is_training': True,
            'group_id': match.group(1),
            'contest_id': match.group(2),
            'default_range': default_range
        }

    match = re.search(cf_gym_pattern, url)
    if match:
        return {
            'platform': 'Codeforces/Gym',
            'base_url': 'https://codeforces.com/gym/{id}/problem/{char}',
            'is_training': False,
            'contest_id': match.group(1),
            'default_range': default_range
        }

    match = re.search(cf_contest_pattern, url)
    if match:
        return {
            'platform': 'Codeforces',
            'base_url': 'https://codeforces.com/contest/{id}/problem/{char}',
            'is_training': False,
            'contest_id': match.group(1),
            'default_range': default_range
        }

    match = re.search(vjudge_pattern, url)
    if match:
        return {
            'platform': 'VJudge',
            'base_url': 'https://vjudge.net/contest/{id}#problem/{char}',
            'is_training': False,
            'contest_id': match.group(1),
            'default_range': default_range
        }

    match = re.search(atcoder_pattern, url)
    if match:
        return {
            'platform': 'AtCoder',
            'base_url': 'https://atcoder.jp/contests/{id}/tasks/{id}_{char}',
            'is_training': False,
            'contest_id': match.group(1),
            'default_range': default_range
        }

    return None

def fetch_problem_names(config, contest_id):
    # For Other platform, use the judge to determine fetch strategy
    fetch_platform = config['platform']
    if fetch_platform == 'Other':
        judge = config.get('judge', '')
        if judge == 'Codeforces Gym':
            fetch_platform = 'Codeforces/Gym'
        elif judge:
            fetch_platform = judge

    try:
        if fetch_platform in ['Codeforces', 'Codeforces/Gym', 'training']:
            api_url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=1"

            req = Request(api_url)
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            if data['status'] != 'OK':
                return {}

            problems = data['result']['problems']
            problem_names = {}
            for problem in problems:
                index = problem['index']
                name = problem['name']
                problem_names[index] = name

            return problem_names

        elif fetch_platform == 'AtCoder':
            url = f"https://atcoder.jp/contests/{contest_id}/tasks"
            req = Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')

            problem_names = {}

            # Pattern to match task rows: captures char and title
            pattern = r'<tr>.*?/tasks/[^"]+_([a-z])"[^>]*>([A-Z])</a>.*?<td[^>]*><a[^>]*>([^<]+)</a></td>'
            matches = re.findall(pattern, html, re.DOTALL)

            for char, _, title in matches:
                problem_names[char.upper()] = title.strip()

            return problem_names

        elif fetch_platform == 'VJudge':
            print(f"{Colors.WARNING}VJudge auto-fetch not supported.{Colors.ENDC}")
            return {}

    except (URLError, Exception) as e:
        print(f"{Colors.WARNING}Could not fetch problem names: {e}{Colors.ENDC}")
        return {}

    return {}

def parse_problems(input_str):
    input_str = input_str.upper()

    if '~' in input_str:
        try:
            start_char, end_char = input_str.split('~')
            start_char = start_char.strip()
            end_char = end_char.strip()

            if len(start_char) == 1 and len(end_char) == 1:
                start_code = ord(start_char)
                end_code = ord(end_char)
                return [chr(i) for i in range(start_code, end_code + 1)]
        except ValueError:
            print(f"{Colors.WARNING}Invalid range format. Using default.{Colors.ENDC}")

    return input_str.replace(',', ' ').split()

def generate_header(problem_char, link, problem_name=None):
    problem_title = f"{problem_char} - {problem_name}" if problem_name else problem_char
    return f"""/**
 * Author:      {AUTHOR_NAME}
 * Problem:     {problem_title}
 * Link:        {link}
 * Status:      ~
 * Created:     {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
 **/

"""

def get_platform_config():
    print(f"{Colors.HEADER}--- Contest Setup ---{Colors.ENDC}")
    print("1. Training (CF Group)")
    print("2. Codeforces (Contest)")
    print("3. Codeforces Gym")
    print("4. VJudge")
    print("5. AtCoder")
    print("6. Other")

    choice = get_input("Choose platform", "1")

    config = {}
    if choice == '1':
        config['platform'] = 'training'
        config['base_url'] = 'https://codeforces.com/group/{group_id}/contest/{id}/problem/{char}'
        config['is_training'] = True
        config['default_range'] = None
    elif choice == '2':
        config['platform'] = 'Codeforces'
        config['base_url'] = 'https://codeforces.com/contest/{id}/problem/{char}'
        config['is_training'] = False
        config['default_range'] = None
    elif choice == '3':
        config['platform'] = 'Codeforces/Gym'
        config['base_url'] = 'https://codeforces.com/gym/{id}/problem/{char}'
        config['is_training'] = False
        config['default_range'] = None
    elif choice == '4':
        config['platform'] = 'VJudge'
        config['base_url'] = 'https://vjudge.net/contest/{id}#problem/{char}'
        config['is_training'] = False
        config['default_range'] = None
    elif choice == '5':
        config['platform'] = 'AtCoder'
        config['base_url'] = 'https://atcoder.jp/contests/{id}/tasks/{id}_{char}'
        config['is_training'] = False
        config['default_range'] = None
    else:
        config['platform'] = 'Other'
        config['is_training'] = False
        config['default_range'] = None

        print(f"\n{Colors.BLUE}Which judge for problem links?{Colors.ENDC}")
        print("1. VJudge")
        print("2. Codeforces Gym")
        print("3. Codeforces (Contest)")
        print("4. AtCoder")
        print("5. None (no links)")

        judge_choice = get_input("Choose judge", "5")

        if judge_choice == '1':
            config['base_url'] = 'https://vjudge.net/contest/{id}#problem/{char}'
            config['judge'] = 'VJudge'
        elif judge_choice == '2':
            config['base_url'] = 'https://codeforces.com/gym/{id}/problem/{char}'
            config['judge'] = 'Codeforces Gym'
        elif judge_choice == '3':
            config['base_url'] = 'https://codeforces.com/contest/{id}/problem/{char}'
            config['judge'] = 'Codeforces'
        elif judge_choice == '4':
            config['base_url'] = 'https://atcoder.jp/contests/{id}/tasks/{id}_{char}'
            config['judge'] = 'AtCoder'
        else:
            config['base_url'] = ''
            config['judge'] = None

    return config

def resolve_training_folder(platform_dir):
    """Generate a unique date-based folder name, adding suffix if needed."""
    base = datetime.now().strftime("%Y.%m.%d")
    candidate = base
    suffix = 2
    while os.path.exists(os.path.join(ROOT_DIR, platform_dir, candidate)):
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate

def collect_manual_config(config):
    """Collect contest_id, folder_name, and group_id for manual/fallback mode."""
    if config['is_training']:
        group_id = get_input("Group ID", DEFAULT_GROUP_ID)
        if not group_id:
            print(f"{Colors.FAIL}Group ID is required.{Colors.ENDC}")
            sys.exit(1)

        contest_id = get_input("Contest ID")
        if not contest_id:
            print(f"{Colors.FAIL}Contest ID is required.{Colors.ENDC}")
            sys.exit(1)

        config['group_id'] = group_id
        return contest_id, resolve_training_folder(config['platform'])
    elif config['platform'] == 'Other':
        folder_name = get_input("Contest name (folder name)")
        if not folder_name:
            print(f"{Colors.FAIL}Contest name is required.{Colors.ENDC}")
            sys.exit(1)

        if config.get('judge'):
            contest_id = get_input(f"{config['judge']} contest ID")
            if not contest_id:
                print(f"{Colors.FAIL}Contest ID is required.{Colors.ENDC}")
                sys.exit(1)
        else:
            contest_id = folder_name

        return contest_id, folder_name
    else:
        contest_id = get_input("Contest ID or Name")
        if not contest_id:
            print(f"{Colors.FAIL}ID is required.{Colors.ENDC}")
            sys.exit(1)
        return contest_id, contest_id

def main():
    if not os.path.exists(TEMPLATE_PATH):
        print(f"{Colors.FAIL}Error: template.cpp not found in root directory.{Colors.ENDC}")
        sys.exit(1)

    with open(TEMPLATE_PATH, 'r') as f:
        template_body = f.read()

    print(f"{Colors.HEADER}--- Contest Setup ---{Colors.ENDC}")
    from_cli = len(sys.argv) > 1
    url = sys.argv[1] if from_cli else get_input("Contest URL (leave empty for manual mode)")

    if url:
        config = parse_contest_url(url)
        if config:
            print(f"{Colors.GREEN}Detected platform: {config['platform']}{Colors.ENDC}")
            if config['is_training']:
                print(f"{Colors.GREEN}Group ID: {config['group_id']}{Colors.ENDC}")
            print(f"{Colors.GREEN}Contest ID: {config['contest_id']}{Colors.ENDC}")

            contest_id = config['contest_id']
            folder_name = resolve_training_folder(config['platform']) if config['is_training'] else contest_id
        else:
            print(f"{Colors.FAIL}Could not parse URL. Switching to manual mode.{Colors.ENDC}")
            config = get_platform_config()
            contest_id, folder_name = collect_manual_config(config)
    else:
        config = get_platform_config()
        contest_id, folder_name = collect_manual_config(config)

    print(f"{Colors.BLUE}Fetching problem names...{Colors.ENDC}")
    problem_names = fetch_problem_names(config, contest_id)

    # Use default_range from URL if available, otherwise use A~E
    default_problems = config.get('default_range', 'A~E')

    if problem_names:
        problems = sorted(problem_names.keys())
        print(f"{Colors.GREEN}Found {len(problem_names)} problems: {', '.join(problems)}{Colors.ENDC}")

        if from_cli:
            print(f"{Colors.GREEN}Using all problems.{Colors.ENDC}")
        else:
            use_all = get_input(f"Use all problems? (y/n)", "y").lower()
            if use_all != 'y':
                problems_input = get_input("Which problems? (e.g.: A~E or A B C)", default_problems)
                problems = parse_problems(problems_input)
    else:
        print(f"{Colors.WARNING}Could not fetch problem names. Please specify manually.{Colors.ENDC}")
        problems_input = get_input("Which problems? (e.g.: A~E or A B C)", default_problems)
        problems = parse_problems(problems_input)

    dest_dir = os.path.join(ROOT_DIR, config['platform'], folder_name)

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"{Colors.GREEN}Folder created: {dest_dir}{Colors.ENDC}")

    for p_char in problems:
        filename = f"{p_char}.cpp"
        filepath = os.path.join(dest_dir, filename)

        problem_url = ""
        if config['base_url']:
            is_atcoder = config['platform'] == 'AtCoder' or config.get('judge') == 'AtCoder'
            char_for_url = p_char.lower() if is_atcoder else p_char
            if config['is_training']:
                problem_url = config['base_url'].format(group_id=config['group_id'], id=contest_id, char=char_for_url)
            else:
                problem_url = config['base_url'].format(id=contest_id, char=char_for_url)

        if os.path.exists(filepath):
             print(f"  {Colors.WARNING}Skipped {filename} (already exists){Colors.ENDC}")
             continue

        problem_name = problem_names.get(p_char)
        header = generate_header(p_char, problem_url, problem_name)
        full_content = header + template_body

        with open(filepath, 'w') as f:
            f.write(full_content)

        print(f"  {Colors.GREEN}+ Created {filename}{Colors.ENDC}")

    print(f"\n{Colors.BLUE}Generating info.md...{Colors.ENDC}")
    from update_info import generate_info_md
    generate_info_md(dest_dir)

    print(f"\n{Colors.BOLD}Setup complete!{Colors.ENDC}")
    link = f"\033]8;;file://{dest_dir}\033\\{dest_dir}\033]8;;\033\\"
    print(f"cd \"{link}\"")

if __name__ == "__main__":
    main()