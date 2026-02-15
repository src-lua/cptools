#!/usr/bin/env python3
"""
Usage: cptools config [options]

Manage cptools configuration. Opens the config file in the default editor.

Options:
  -e, --editor EDITOR    Use specific editor (overrides $EDITOR and fallback chain)

Examples:
  cptools config              # Use default editor with fallback chain
  cptools config -e nano      # Force use of nano
  cptools config --editor vim # Force use of vim
"""
import os
import sys
import argparse
import subprocess

from cptools.lib.io import info, error
from cptools.lib.config import ensure_config, get_config_path

def get_parser():
    """Creates and returns the argparse parser for the config command."""
    parser = argparse.ArgumentParser(description="Manage cptools configuration.")
    parser.add_argument('-e', '--editor', help='Use specific editor (e.g., nano, vim, emacs)')
    return parser

def find_editor():
    """
    Find an available text editor with user-friendly fallback chain.

    Priority order:
    1. $EDITOR environment variable (user preference)
    2. nano (beginner-friendly, simple to use)
    3. vim (powerful, widely available)
    4. vi (POSIX standard, always available)
    5. emacs (alternative powerful editor)

    Returns:
        tuple: (editor_command, is_vim_like) where is_vim_like indicates if brief help should be shown
    """
    # Respect user's explicit preference
    if "EDITOR" in os.environ:
        editor = os.environ["EDITOR"]
        # Check if it's actually available
        try:
            result = subprocess.run(
                ["which", editor],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                is_vim_like = any(vim in editor.lower() for vim in ['vim', 'vi', 'nvim'])
                return (editor, is_vim_like)
        except Exception:
            pass

    # Try fallback chain (user-friendly first)
    fallback_editors = [
        ('nano', False),
        ('vim', True),
        ('vi', True),
        ('emacs', False),
    ]

    for editor, is_vim_like in fallback_editors:
        try:
            result = subprocess.run(
                ["which", editor],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return (editor, is_vim_like)
        except Exception:
            continue

    # Last resort fallback
    return ('vi', True)


def show_vim_help():
    """Display brief vim usage help for beginners."""
    from cptools.lib.io import Colors, bold

    print()
    bold("Vim Quick Start:")
    print(f"{Colors.BOLD}i{Colors.ENDC}          - Enter insert mode (start editing)")
    print(f"{Colors.BOLD}Esc{Colors.ENDC}        - Exit insert mode (back to normal mode)")
    print(f"{Colors.BOLD}:w{Colors.ENDC}         - Save file")
    print(f"{Colors.BOLD}:q{Colors.ENDC}         - Quit")
    print(f"{Colors.BOLD}:wq{Colors.ENDC}        - Save and quit")
    print(f"{Colors.BOLD}:q!{Colors.ENDC}        - Quit without saving")
    print()


def run():
    parser = get_parser()
    args = parser.parse_args()

    ensure_config()
    path = get_config_path()

    # Use --editor flag if provided, otherwise find available editor
    if args.editor:
        editor = args.editor
        is_vim_like = any(vim in editor.lower() for vim in ['vim', 'vi', 'nvim'])
    else:
        editor, is_vim_like = find_editor()

    info(f"Opening config: {path}")
    info(f"Editor: {editor}")

    # Show help for vim-like editors
    if is_vim_like:
        show_vim_help()

    try:
        subprocess.run([editor, path])
    except FileNotFoundError:
        error(f"Editor '{editor}' not found.")
        error("Please install a text editor (nano, vim, or emacs) or set $EDITOR.")
        sys.exit(1)

