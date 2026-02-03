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

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        return 0
    fi

    local command="${COMP_WORDS[1]}"
    case "${command}" in
%(cases)s
        *)
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
            local -a commands
            commands=(
%(commands_desc)s
            )
            _describe -t commands 'cptools command' commands
            ;;
        (args)
            case $line[1] in
%(cases)s
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
    commands = " ".join(data.keys())
    cases = ""
    for cmd, info in data.items():
        opts = " ".join([o['long'] for o in info['options']])
        if not opts: continue
        cases += f"        {cmd})\n            COMPREPLY=( $(compgen -W \"{opts}\" -- ${{cur}}) )\n            return 0\n            ;;\n"
    
    return BASH_TEMPLATE % {'commands': commands, 'cases': cases}

def generate_zsh(data):
    commands_desc_list = []
    for cmd, info in data.items():
        desc = info['desc'].replace("'", "'\\''")
        commands_desc_list.append(f"        '{cmd}:{desc}'")
    commands_desc = "\n".join(commands_desc_list)
    cases = ""
    for cmd, info in data.items():
        opts = []
        for o in info['options']:
            help_text = o['help'].replace("'", "'\\''")
            if o['short']:
                opts.append(f"'({o['short']} {o['long']})'{{'{o['short']}','{o['long']}'}}'[{help_text}]'")
            else:
                opts.append(f"'{o['long']}[{help_text}]'")
        
        if opts:
            opts_str = " ".join(opts)
            cases += f"                {cmd})\n                    _arguments \\\n                        {opts_str}\n                    ;;\n"
        else:
            cases += f"                {cmd})\n                    _arguments\n                    ;;\n"
            
    return ZSH_TEMPLATE % {'commands_desc': commands_desc, 'cases': cases}

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
                print(f"{Colors.GREEN}✓ Completion already installed in {rc_file}{Colors.ENDC}")
                return

    with open(rc_file, 'a') as f:
        f.write(f"\n# cptools completion\n{source_line}\n")
    
    print(f"{Colors.GREEN}✓ Installed to {filepath}{Colors.ENDC}")
    print(f"{Colors.GREEN}✓ Added source line to {rc_file}{Colors.ENDC}")
    print(f"{Colors.BOLD}Please restart your shell.{Colors.ENDC}")

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
