"""
Display and formatting utilities for cptools.

This module provides utilities for displaying problem statuses and formatting output.
"""


def get_status_emoji(status):
    """
    Map status to emoji.

    Args:
        status: Status string (e.g., 'AC', 'WA', '~', 'WIP')

    Returns:
        Emoji string representing the status

    Examples:
        >>> get_status_emoji('AC')
        '✅'
        >>> get_status_emoji('WA')
        '⚠️'
        >>> get_status_emoji('~')
        '⬜'
    """
    status_lower = status.lower().strip()

    # Pending / Not attempted
    if status_lower in ['~', 'pending', 'not attempted', '']:
        return '⬜'

    # Solved/Accepted
    elif status_lower in ['solved', 'accepted', 'ac']:
        return '✅'

    # In Progress
    elif status_lower in ['attempting', 'in progress', 'wip']:
        return '🔄'

    # Wrong Answer
    elif status_lower in ['wa', 'wrong answer']:
        return '⚠️'

    # Time Limit Exceeded
    elif status_lower in ['tle', 'time limit', 'time limit exceeded']:
        return '⏱️'

    # Memory Limit Exceeded
    elif status_lower in ['mle', 'memory limit', 'memory limit exceeded']:
        return '💾'

    # Runtime Error
    elif status_lower in ['re', 'runtime error']:
        return '💥'

    # Not solved / Unsolved
    else:
        return '❌'
