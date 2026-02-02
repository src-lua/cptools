#!/usr/bin/env python3
"""
Usage: cptools config

Manage cptools configuration. Opens the config file in the default editor.

Examples:
  cptools config
"""
import os
import sys
import argparse
import subprocess

from lib.io import info, error
from lib.config import ensure_config, get_config_path

def get_parser():
    """Creates and returns the argparse parser for the config command."""
    parser = argparse.ArgumentParser(description="Manage cptools configuration.")
    return parser

def run():
    parser = get_parser()
    args = parser.parse_args()

    ensure_config()

    editor = os.environ.get("EDITOR", "vi")
    path = get_config_path()
    info(f"Opening config: {path}")

    try:
        subprocess.run([editor, path])
    except FileNotFoundError:
        error(f"Editor '{editor}' not found. Set $EDITOR.")
        sys.exit(1)

