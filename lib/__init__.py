"""
CPTools library - Core functionality for competitive programming tools.

This package provides:
- parsing: Problem range/URL parsing utilities
- http_utils: HTTP request utilities
- fileops: File operations and header management
- compiler: C++ compilation utilities
- judges: Platform/judge abstractions (Phase 2)
"""

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
    JUDGES,
    detect_judge,
)

__all__ = [
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
    'JUDGES',
    'detect_judge',
]
