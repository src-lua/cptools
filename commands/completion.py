#!/usr/bin/env python3
"""
Usage: cptools completion [options]

Generate and install shell completion scripts for bash and zsh.

Options:
  --install       Install completion for your current shell (auto-detected)
  --shell SHELL   Output completion script for specific shell (bash or zsh)

Examples:
  cptools completion --install        # Install for current shell
  cptools completion --shell bash     # Generate bash completion script
  cptools completion --shell zsh      # Generate zsh completion script

Installation:
  1. Run: cptools completion --install
  2. Restart your shell
  3. Enjoy tab completion for all cptools commands and flags!

Features:
  - Command completion: Completes cptools subcommands
  - Flag completion: Completes command-specific flags (--flag)
  - File completion: Completes .cpp files for commands like add, rm, mark, open, test, bundle
  - Directory completion: Completes directories for commands like update, new
"""
import os
import sys
import re
import argparse
from lib.io import Colors
from lib import get_command_modules

BASH_TEMPLATE = r"""
_cptools_completion() {
    local cur prev words cword
    if declare -f _init_completion >/dev/null; then
        _init_completion -n : || return
    else
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"
    fi

    local commands="%(commands)s"
    local global_flags="-h --help -v --version"

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        if [[ ${cur} == -* ]]; then
            COMPREPLY=( $(compgen -W "${global_flags}" -- ${cur}) )
        else
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        fi
        return 0
    fi

    local command="${COMP_WORDS[1]}"

    # Commands that accept files as positional arguments
    case "${command}" in
        add|rm|mark|open|test|bundle)
            # Complete with .cpp files or flags
            if [[ ${cur} == -* ]]; then
                # Complete flags for this specific command
                local opts=""
                case "${command}" in
%(file_cmd_flags)s
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                # Complete with .cpp files
                COMPREPLY=( $(compgen -f -X '!*.cpp' -- ${cur}) )
            fi
            return 0
            ;;
        update|new)
            # Complete with directories or flags
            if [[ ${cur} == -* ]]; then
                # Complete flags for this specific command
                local opts=""
                case "${command}" in
%(dir_cmd_flags)s
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            else
                # Complete with directories
                COMPREPLY=( $(compgen -d -- ${cur}) )
            fi
            return 0
            ;;
        *)
            # For other commands, just complete flags
            case "${command}" in
%(other_flags)s
            esac
            ;;
    esac
}
complete -F _cptools_completion cptools cpt
"""

ZSH_TEMPLATE = r"""
#compdef cptools cpt

_cptools() {
    local context state state_descr line
    typeset -A opt_args

    _arguments -C \
        '1: :->command' \
        '*:: :->args'

    case $state in
        (command)
            local -a commands flags
            commands=(
%(commands_desc)s
            )
            flags=(
                '--help:Show help message'
                '-h:Show help message'
                '--version:Show version information'
                '-v:Show version information'
            )
            _describe -t commands 'cptools command' commands
            _describe -t flags 'global flags' flags
            ;;
        (args)
            case $line[1] in
%(file_cases)s
%(dir_cases)s
%(other_cases)s
            esac
            ;;
    esac
}

compdef _cptools cptools cpt
"""

def get_commands_data():
    data = {}
    command_modules = get_command_modules()

    for name, mod in command_modules.items():
        try:
            # Get parser via get_parser() for robust introspection
            parser = mod.get_parser()
            desc = parser.description or "No description"
            options = []
            for action in parser._actions:
                # Skip positional arguments and the default help flag
                if not action.option_strings or '-h' in action.option_strings or '--help' in action.option_strings:
                    continue

                long_flag = next((s for s in action.option_strings if s.startswith('--')), None)
                short_flag = next((s for s in action.option_strings if s.startswith('-') and not s.startswith('--')), None)

                if long_flag:
                    options.append({
                        'short': short_flag,
                        'long': long_flag,
                        'help': action.help or ''
                    })
            data[name] = {'desc': desc, 'options': options}

        except Exception:
            continue
            
    return data

def generate_bash(data):
    """
    Generate bash completion script with intelligent file/directory completion.

    The generated script provides context-aware completion:
    - For file commands (add, rm, mark, open, test, bundle): Completes .cpp files
    - For directory commands (update, new): Completes directories
    - For all commands: Completes flags when input starts with -

    Args:
        data: Dict of command data from get_commands_data()

    Returns:
        Complete bash completion script as string
    """
    commands = " ".join(data.keys())

    # Commands that accept .cpp files as positional arguments
    file_commands = ['add', 'rm', 'mark', 'open', 'test', 'bundle']
    # Commands that accept directories as positional arguments
    dir_commands = ['update', 'new']

    # Generate flag cases for file commands
    file_cmd_flags = ""
    for cmd in file_commands:
        if cmd in data:
            opts = " ".join([o['long'] for o in data[cmd]['options']])
            if opts:
                file_cmd_flags += f"                    {cmd})\n                        opts=\"{opts}\"\n                        ;;\n"

    # Generate flag cases for directory commands
    dir_cmd_flags = ""
    for cmd in dir_commands:
        if cmd in data:
            opts = " ".join([o['long'] for o in data[cmd]['options']])
            if opts:
                dir_cmd_flags += f"                    {cmd})\n                        opts=\"{opts}\"\n                        ;;\n"

    # Generate flag cases for other commands
    other_flags = ""
    for cmd, info in data.items():
        if cmd in file_commands or cmd in dir_commands:
            continue
        opts = " ".join([o['long'] for o in info['options']])
        if opts:
            other_flags += f"                {cmd})\n                    COMPREPLY=( $(compgen -W \"{opts}\" -- ${{cur}}) )\n                    return 0\n                    ;;\n"

    return BASH_TEMPLATE % {
        'commands': commands,
        'file_cmd_flags': file_cmd_flags,
        'dir_cmd_flags': dir_cmd_flags,
        'other_flags': other_flags
    }

def generate_zsh(data):
    """
    Generate zsh completion script with intelligent file/directory completion.

    The generated script provides context-aware completion:
    - For file commands (add, rm, mark, open, test, bundle): Completes .cpp files using _files -g "*.cpp"
    - For directory commands (update, new): Completes directories using _files -/
    - For all commands: Completes flags with descriptions

    Args:
        data: Dict of command data from get_commands_data()

    Returns:
        Complete zsh completion script as string
    """
    commands_desc_list = []
    for cmd, info in data.items():
        desc = info['desc'].replace("'", "'\\''")
        commands_desc_list.append(f"        '{cmd}:{desc}'")
    commands_desc = "\n".join(commands_desc_list)

    # Commands that accept .cpp files as positional arguments
    file_commands = ['add', 'rm', 'mark', 'open', 'test', 'bundle']
    # Commands that accept directories as positional arguments
    dir_commands = ['update', 'new']

    # Generate individual cases for file commands
    file_cases = ""
    for cmd in file_commands:
        if cmd in data:
            opts = []
            for o in data[cmd]['options']:
                help_text = o['help'].replace("'", "'\\''")
                if o['short']:
                    opts.append(f"'({o['short']} {o['long']})'{{'{o['short']}','{o['long']}'}}'[{help_text}]'")
                else:
                    opts.append(f"'{o['long']}[{help_text}]'")

            if opts:
                opts_str = " \\\n                        ".join(opts)
                file_cases += f"                {cmd})\n                    _arguments \\\n                        {opts_str} \\\n                        '*:cpp files:_files -g \"*.cpp\"'\n                    ;;\n"
            else:
                file_cases += f"                {cmd})\n                    _files -g \"*.cpp\"\n                    ;;\n"

    # Generate individual cases for directory commands
    dir_cases = ""
    for cmd in dir_commands:
        if cmd in data:
            opts = []
            for o in data[cmd]['options']:
                help_text = o['help'].replace("'", "'\\''")
                if o['short']:
                    opts.append(f"'({o['short']} {o['long']})'{{'{o['short']}','{o['long']}'}}'[{help_text}]'")
                else:
                    opts.append(f"'{o['long']}[{help_text}]'")

            if opts:
                opts_str = " \\\n                        ".join(opts)
                dir_cases += f"                {cmd})\n                    _arguments \\\n                        {opts_str} \\\n                        '*:directories:_files -/'\n                    ;;\n"
            else:
                dir_cases += f"                {cmd})\n                    _files -/\n                    ;;\n"

    # Generate cases for other commands
    other_cases = ""
    for cmd, info in data.items():
        if cmd in file_commands or cmd in dir_commands:
            continue

        opts = []
        for o in info['options']:
            help_text = o['help'].replace("'", "'\\''")
            if o['short']:
                opts.append(f"'({o['short']} {o['long']})'{{'{o['short']}','{o['long']}'}}'[{help_text}]'")
            else:
                opts.append(f"'{o['long']}[{help_text}]'")

        if opts:
            opts_str = " \\\n                        ".join(opts)
            other_cases += f"                {cmd})\n                    _arguments \\\n                        {opts_str}\n                    ;;\n"
        else:
            other_cases += f"                {cmd})\n                    _arguments\n                    ;;\n"

    return ZSH_TEMPLATE % {
        'commands_desc': commands_desc,
        'file_cases': file_cases,
        'dir_cases': dir_cases,
        'other_cases': other_cases
    }

def install(shell):
    if shell not in ['bash', 'zsh']:
        print(f"{Colors.FAIL}Error: Unsupported shell '{shell}'{Colors.ENDC}")
        sys.exit(1)

    data = get_commands_data()
    script = generate_bash(data) if shell == 'bash' else generate_zsh(data)
    
    config_dir = os.path.expanduser("~/.config/cptools")
    os.makedirs(config_dir, exist_ok=True)
    
    filepath = os.path.join(config_dir, f"completion.{shell}")
    with open(filepath, 'w') as f:
        f.write(script)
    
    rc_file = os.path.expanduser(f"~/.{shell}rc")
    source_line = f"source {filepath}"
    
    if os.path.exists(rc_file):
        with open(rc_file, 'r') as f:
            if source_line in f.read():
                print(f"{Colors.GREEN}✓ Completion script updated at {filepath}{Colors.ENDC}")
                print(f"{Colors.GREEN}✓ Already sourced in {rc_file}{Colors.ENDC}")
                print(f"\n{Colors.BOLD}{Colors.WARNING}⚠ Please restart your terminal or run:{Colors.ENDC}")
                print(f"  {Colors.BLUE}source {rc_file}{Colors.ENDC}\n")
                return

    with open(rc_file, 'a') as f:
        f.write(f"\n# cptools completion\n{source_line}\n")

    print(f"{Colors.GREEN}✓ Installed to {filepath}{Colors.ENDC}")
    print(f"{Colors.GREEN}✓ Added source line to {rc_file}{Colors.ENDC}")
    print(f"\n{Colors.BOLD}{Colors.WARNING}⚠ Please restart your terminal or run:{Colors.ENDC}")
    print(f"  {Colors.BLUE}source {rc_file}{Colors.ENDC}\n")

def get_parser():
    """Creates and returns the argparse parser for the completion command."""
    parser = argparse.ArgumentParser(description="Generate and install shell completion scripts.")
    parser.add_argument('--install', action='store_true', help="Install completion for the detected shell")
    parser.add_argument('--shell', choices=['bash', 'zsh'], help="Output completion script for specific shell")
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    if args.install:
        shell = os.path.basename(os.environ.get('SHELL', 'bash'))
        install(shell)
    elif args.shell:
        data = get_commands_data()
        print(generate_bash(data) if args.shell == 'bash' else generate_zsh(data))
    else:
        parser.print_help()
