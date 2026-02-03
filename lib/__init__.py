"""
CPTools library - Core functionality for competitive programming tools.

This package provides:
- parsing: Problem range/URL parsing utilities
- http_utils: HTTP request utilities
- fileops: File operations and header management
- compiler: C++ compilation utilities
- judges: Platform/judge abstractions (Phase 2)
- io: IO and logging utilities
- config: Configuration management
- commands: Command modules registry
"""

# Custom Exceptions
class CptoolsError(Exception):
    """Base exception for all cptools errors."""
    pass

class PlatformError(CptoolsError):
    """Raised when there's an error with a platform/judge (network, parsing, etc.)."""
    pass

class FileOperationError(CptoolsError):
    """Raised when there's an error with file operations."""
    pass

class CompilationError(CptoolsError):
    """Raised when compilation fails."""
    pass

class ParsingError(CptoolsError):
    """Raised when parsing fails (URL, problem range, etc.)."""
    pass

# Parsing utilities
from .parsing import (
    parse_problem_range,
    parse_problem_url,
    parse_contest_url,
)

# HTTP utilities
from .http_utils import (
    fetch_url,
    fetch_json,
    DEFAULT_HEADERS,
)

# File operations
from .fileops import (
    ProblemHeader,
    generate_header,
    read_problem_header,
    update_problem_status,
    find_samples,
    save_samples,
    next_test_index,
    create_problem_file,
    find_file_case_insensitive,
)

# Compiler utilities
from .compiler import (
    CompilationResult,
    compile_cpp,
    compile_from_config,
)

# Judge/platform abstractions
from .judges import (
    ProblemInfo,
    SampleTest,
    Judge,
    CodeforcesJudge,
    AtCoderJudge,
    CSESJudge,
    YosupoJudge,
    VJudgeJudge,
    ALL_JUDGES,
    detect_judge,
)

# IO and logging utilities
from .io import (
    Colors,
    log,
    out,
    error,
    success,
    warning,
    info,
    header,
    bold,
)

# Configuration
from .config import (
    load_config,
    ensure_config,
    get_config_path,
)

# Display utilities
from .display_utils import (
    get_status_emoji,
)

# Path utilities
from .path_utils import (
    detect_platform_from_path,
)

# Command modules registry
def get_command_modules():
    """
    Returns a dict mapping command names to their modules.
    Import is done lazily to avoid circular dependencies.
    """
    from commands import (
        new, add, rm, mark, status, fetch, clean, update,
        init, config, commit, bundle, stress, test, hash
    )
    from commands import open as open_cmd
    from commands import completion

    return {
        'new': new,
        'add': add,
        'rm': rm,
        'mark': mark,
        'status': status,
        'open': open_cmd,
        'test': test,
        'fetch': fetch,
        'stress': stress,
        'clean': clean,
        'update': update,
        'init': init,
        'config': config,
        'commit': commit,
        'bundle': bundle,
        'hash': hash,
        'completion': completion,
    }

__all__ = [
    # Exceptions
    'CptoolsError',
    'PlatformError',
    'FileOperationError',
    'CompilationError',
    'ParsingError',
    # Parsing
    'parse_problem_range',
    'parse_problem_url',
    'parse_contest_url',
    # HTTP
    'fetch_url',
    'fetch_json',
    'DEFAULT_HEADERS',
    # File operations
    'ProblemHeader',
    'generate_header',
    'read_problem_header',
    'update_problem_status',
    'find_samples',
    'save_samples',
    'next_test_index',
    'create_problem_file',
    'find_file_case_insensitive',
    # Compiler
    'CompilationResult',
    'compile_cpp',
    'compile_from_config',
    # Judges
    'ProblemInfo',
    'SampleTest',
    'Judge',
    'CodeforcesJudge',
    'AtCoderJudge',
    'CSESJudge',
    'YosupoJudge',
    'VJudgeJudge',
    'ALL_JUDGES',
    'detect_judge',
    # IO and logging
    'Colors',
    'log',
    'out',
    'error',
    'success',
    'warning',
    'info',
    'header',
    'bold',
    # Config
    'load_config',
    'ensure_config',
    'get_config_path',
    # Display utilities
    'get_status_emoji',
    # Path utilities
    'detect_platform_from_path',
    # Commands
    'get_command_modules',
]
