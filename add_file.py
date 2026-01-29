#!/usr/bin/env python3
"""
Create a new .cpp file with the standard header and template.

Usage:
    python3 add_file.py <name> [directory]

Examples:
    python3 add_file.py A2              # creates A2.cpp in current dir
    python3 add_file.py B-brute         # creates B-brute.cpp
    python3 add_file.py A2 /path/to/dir # creates in specific directory
"""
import os
import sys
from datetime import datetime
from colors import Colors

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "template.cpp")
AUTHOR_NAME = "Lua"

def generate_header(name):
    return f"""/**
 * Author:      {AUTHOR_NAME}
 * Problem:     {name}
 * Link:
 * Status:      ~
 * Created:     {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
 **/

"""

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.FAIL}Usage: add_file.py <name> [directory]{Colors.ENDC}")
        print(f"  Examples: add_file.py A2, add_file.py B-brute")
        sys.exit(1)

    name = sys.argv[1]
    directory = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()

    if not os.path.isdir(directory):
        print(f"{Colors.FAIL}Error: {directory} is not a valid directory.{Colors.ENDC}")
        sys.exit(1)

    if not os.path.exists(TEMPLATE_PATH):
        print(f"{Colors.FAIL}Error: template.cpp not found.{Colors.ENDC}")
        sys.exit(1)

    # Add .cpp if not present
    filename = name if name.endswith('.cpp') else f"{name}.cpp"
    filepath = os.path.join(directory, filename)

    if os.path.exists(filepath):
        print(f"{Colors.WARNING}{filename} already exists.{Colors.ENDC}")
        sys.exit(1)

    with open(TEMPLATE_PATH, 'r') as f:
        template_body = f.read()

    # Try to inherit link from sibling files (same contest)
    link = ""
    base_letter = name[0].upper()
    sibling = os.path.join(directory, f"{base_letter}.cpp")
    if os.path.exists(sibling):
        with open(sibling, 'r') as f:
            for line in f.read(500).split('\n'):
                if 'Link:' in line:
                    link = line.split('Link:')[1].strip().replace('*/', '').strip()
                    break

    header = generate_header(name)
    if link:
        header = header.replace("Link:        ", f"Link:        {link}")

    with open(filepath, 'w') as f:
        f.write(header + template_body)

    print(f"{Colors.GREEN}+ Created {filename}{Colors.ENDC}")
    if link:
        print(f"{Colors.BLUE}  Inherited link from {base_letter}.cpp{Colors.ENDC}")

    # Update info.md
    from update_info import generate_info_md
    generate_info_md(directory)

if __name__ == "__main__":
    main()
