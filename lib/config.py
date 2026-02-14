"""
Configuration management for cptools.
"""
import os
import json

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "cptools")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "author": "Dev",
    "default_group_id": "yc7Yxny414",
    "compiler": "g++",
    "compiler_flags": ["-O2", "-std=c++17"],
    "cookie_cache_enabled": True,
    "cookie_cache_max_age_hours": 24,  # -1 = never expire (only refresh on auth failure)
    "preferred_browser": None,  # None = auto-detect, or "firefox", "chrome", etc.
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