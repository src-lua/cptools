#!/usr/bin/env python3
"""
Manage cptools configuration.

Usage:
    cptools config              Open config file in $EDITOR
"""
import os
import sys
import json
import subprocess

from .common import Colors

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "cptools")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "author": "Lua",
    "default_group_id": "yc7Yxny414",
    "compiler": "g++",
    "compiler_flags": ["-O2", "-std=c++17"],
}

def get_config_path():
    return CONFIG_PATH

def ensure_config():
    """Create config file with defaults if it doesn't exist."""
    if os.path.exists(CONFIG_PATH):
        return

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(DEFAULTS, f, indent=4)
        f.write('\n')

def load_config():
    """Load config, merging with defaults for any missing keys."""
    ensure_config()
    try:
        with open(CONFIG_PATH, 'r') as f:
            user_config = json.load(f)
    except (json.JSONDecodeError, IOError):
        user_config = {}

    config = dict(DEFAULTS)
    config.update(user_config)
    return config

def main():
    ensure_config()

    editor = os.environ.get("EDITOR", "vi")
    print(f"{Colors.BLUE}Opening config: {CONFIG_PATH}{Colors.ENDC}")

    try:
        subprocess.run([editor, CONFIG_PATH])
    except FileNotFoundError:
        print(f"{Colors.FAIL}Editor '{editor}' not found. Set $EDITOR.{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
