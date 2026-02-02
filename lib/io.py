"""
IO and logging utilities for cptools.

This module provides:
- Colors: ANSI color codes for terminal output
- Output functions for logging, errors, warnings, data output, etc.
- docs(): Standard help/usage handler
"""
import sys


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def log(*args, **kwargs):
    """
    Print to stderr for logging messages.

    This allows stdout redirection to only capture actual program output,
    while log messages go to stderr.

    Examples:
        >>> log("Compiling...")
        >>> log("Found", len(files), "files")
    """
    print(*args, file=sys.stderr, **kwargs)


def out(*args, **kwargs):
    """
    Print to stdout for actual program output/data.

    Use this for output that should be capturable via stdout redirection.

    Examples:
        >>> out("result data")
        >>> out(json.dumps(data))
    """
    print(*args, **kwargs)


def error(message, **kwargs):
    """
    Print an error message to stderr in red.

    Args:
        message: The error message to display
        **kwargs: Additional arguments to pass to print()

    Examples:
        >>> error("File not found")
        >>> error(f"Invalid input: {value}")
    """
    log(f"{Colors.FAIL}{message}{Colors.ENDC}", **kwargs)


def success(message, **kwargs):
    """
    Print a success message to stderr in green.

    Args:
        message: The success message to display
        **kwargs: Additional arguments to pass to print()

    Examples:
        >>> success("File created successfully")
        >>> success(f"+ {filename}")
    """
    log(f"{Colors.GREEN}{message}{Colors.ENDC}", **kwargs)


def warning(message, **kwargs):
    """
    Print a warning message to stderr in yellow.

    Args:
        message: The warning message to display
        **kwargs: Additional arguments to pass to print()

    Examples:
        >>> warning("File already exists")
        >>> warning(f"! {filename} not found")
    """
    log(f"{Colors.WARNING}{message}{Colors.ENDC}", **kwargs)


def info(message, **kwargs):
    """
    Print an info message to stderr in blue.

    Args:
        message: The info message to display
        **kwargs: Additional arguments to pass to print()

    Examples:
        >>> info("Compiling...")
        >>> info(f"Running {count} tests...")
    """
    log(f"{Colors.BLUE}{message}{Colors.ENDC}", **kwargs)


def header(message, **kwargs):
    """
    Print a header message to stderr in magenta.

    Args:
        message: The header message to display
        **kwargs: Additional arguments to pass to print()

    Examples:
        >>> header("--- Fetching Samples ---")
        >>> header("=== Test Results ===")
    """
    log(f"{Colors.HEADER}{message}{Colors.ENDC}", **kwargs)


def bold(message, **kwargs):
    """
    Print a bold message to stderr.

    Args:
        message: The message to display in bold
        **kwargs: Additional arguments to pass to print()

    Examples:
        >>> bold("Summary:")
        >>> bold(f"{passed}/{total} tests passed")
    """
    log(f"{Colors.BOLD}{message}{Colors.ENDC}", **kwargs)
