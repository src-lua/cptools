"""
Path and directory utilities for cptools.

This module provides utilities for detecting platforms from paths and other
path-related operations.
"""
from pathlib import Path


def detect_platform_from_path(path):
    """
    Detect contest platform from directory structure.

    Args:
        path: File or directory path

    Returns:
        Tuple of (platform_label, contest_name)

    Examples:
        >>> detect_platform_from_path('/home/user/Codeforces/1234/A.cpp')
        ('Codeforces', '1234')
        >>> detect_platform_from_path('/home/user/AtCoder/abc123')
        ('AtCoder', 'abc123')
        >>> detect_platform_from_path('/home/user/Codeforces/Gym/12345')
        ('Codeforces Gym', '12345')
    """
    parts = Path(path).parts

    platform_map = {
        'Trainings': 'Trainings',
        'Codeforces': 'Codeforces',
        'vJudge': 'vJudge',
        'AtCoder': 'AtCoder',
        'Yosupo': 'Yosupo',
        'Other': 'Other',
    }

    # Check for Codeforces/Gym (nested platform dir)
    if 'Codeforces' in parts:
        idx = parts.index('Codeforces')
        if idx + 1 < len(parts) and parts[idx + 1] == 'Gym':
            if idx + 2 < len(parts):
                return 'Codeforces Gym', parts[idx + 2]
            return 'Codeforces Gym', Path(path).name

    # Other/ uses the subfolder name as the display name
    if 'Other' in parts:
        idx = parts.index('Other')
        if idx + 1 < len(parts):
            name = parts[idx + 1]
            return name, name

    for key, label in platform_map.items():
        if key in parts:
            idx = parts.index(key)
            if idx + 1 < len(parts):
                return label, parts[idx + 1]

    return 'Contest', Path(path).name
