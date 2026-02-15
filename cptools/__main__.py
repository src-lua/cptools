#!/usr/bin/env python3
"""
cptools - Competitive Programming Tools

Main entry point for the cptools CLI application.
"""
import sys
from cptools.lib.io import Colors, error, log
from cptools.lib import get_command_modules

# Get command modules registry
COMMAND_MODULES = get_command_modules()

def get_command_description(module):
    """Get command description from module's argparse parser."""
    try:
        parser = module.get_parser()
        return parser.description or "No description"
    except (AttributeError, Exception):
        return "No description"

def print_help():
    """Print help message with available commands."""
    print(f"{Colors.BOLD}cptools{Colors.ENDC} - Competitive Programming Tools\n")
    print(f"{Colors.BOLD}Usage:{Colors.ENDC} cptools <command> [args]\n")
    print(f"{Colors.BOLD}Commands:{Colors.ENDC}")

    for cmd_name, module in COMMAND_MODULES.items():
        desc = get_command_description(module)
        # Truncate description if too long for clean display
        if len(desc) > 80:
            desc = desc[:77] + "..."
        print(f"  {Colors.GREEN}{cmd_name:<12}{Colors.ENDC}  {desc}")

    print(f"\nRun {Colors.BLUE}cptools <command> --help{Colors.ENDC} for more info on a command.")
    print(f"\n{Colors.BOLD}Tip:{Colors.ENDC} Enable shell completion with {Colors.BLUE}cptools completion --install{Colors.ENDC}")

def print_version():
    """Print version information."""
    from importlib.metadata import version
    try:
        __version__ = version("lgf-cptools")
    except Exception:
        __version__ = "unknown"

    print(f"{Colors.BOLD}{Colors.HEADER}cptools {__version__}{Colors.ENDC}")
    print(f"Copyright (C) 2026 Lua Guimarães Fernandes")
    print(f"License MIT <https://opensource.org/licenses/MIT>")
    print(f"This is free software; you are free to change and redistribute it.")

def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print_help()
        sys.exit(0)

    if sys.argv[1] in ['-v', '--version']:
        print_version()
        sys.exit(0)

    command = sys.argv[1]

    # Check if command exists
    if command not in COMMAND_MODULES:
        error(f"Unknown command: {command}")
        log()
        print_help()
        sys.exit(1)

    # Rewrite sys.argv so the sub-script sees its own args
    sys.argv = [command] + sys.argv[2:]

    # Execute the command
    COMMAND_MODULES[command].run()

if __name__ == "__main__":
    main()
