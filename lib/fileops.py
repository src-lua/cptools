"""
File operations for C++ source files and problem metadata.

This module handles:
- Reading/writing C++ file headers with problem metadata
- Managing sample test files (.in/.out)
- File creation from templates
"""
import os
import re
import glob
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProblemHeader:
    """Problem metadata extracted from C++ file header."""
    problem: Optional[str]
    link: Optional[str]
    status: str
    created: Optional[str]


def generate_header(problem_id, link="", problem_name=None, author="Unknown",
                   status="~", created=None):
    """
    Generate standard C++ file header with problem metadata.

    Args:
        problem_id: Problem identifier (e.g., "A", "1234A")
        link: Problem URL (default: empty)
        problem_name: Full problem name for title (default: None)
        author: Author name from config (default: "Unknown")
        status: Problem status (default: "~" for pending)
        created: Creation timestamp (default: now)

    Returns:
        Formatted header string with /** ... **/

    Examples:
        >>> header = generate_header("A", "https://example.com/A", "Problem A", "Alice")
        >>> print(header)
        /**
         * Author:      Alice
         * Problem:     A - Problem A
         * Link:        https://example.com/A
         * Status:      ~
         * Created:     31-01-2026 12:00:00
         **/
        <BLANKLINE>
    """
    if created is None:
        created = datetime.now()

    # Format creation time
    if isinstance(created, datetime):
        created_str = created.strftime("%d-%m-%Y %H:%M:%S")
    else:
        created_str = created

    # Format problem title
    problem_title = f"{problem_id} - {problem_name}" if problem_name else problem_id

    return f"""/**
 * Author:      {author}
 * Problem:     {problem_title}
 * Link:        {link}
 * Status:      {status}
 * Created:     {created_str}
 **/

"""


def read_problem_header(filepath):
    """
    Extract problem metadata from C++ file header.

    Reads first 500 chars and parses comment block for metadata fields.

    Args:
        filepath: Path to .cpp file

    Returns:
        ProblemHeader object, or None if file cannot be read

    Examples:
        >>> header = read_problem_header("A.cpp")
        >>> header.status
        'AC'
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read(500)  # Read first 500 chars (header should be there)

        info = {
            'problem': None,
            'link': None,
            'status': '~',
            'created': None
        }

        for line in content.split('\n'):
            if 'Problem:' in line:
                info['problem'] = line.split('Problem:')[1].strip().replace('*/', '').strip()
            elif 'Link:' in line:
                info['link'] = line.split('Link:')[1].strip().replace('*/', '').strip()
            elif 'Status:' in line:
                info['status'] = line.split('Status:')[1].strip().replace('*/', '').strip()
            elif 'Created:' in line:
                info['created'] = line.split('Created:')[1].strip().replace('*/', '').strip()

        return ProblemHeader(**info)
    except Exception:
        return None


def update_problem_status(filepath, new_status):
    """
    Update status field in a C++ file header.

    Args:
        filepath: Path to .cpp file
        new_status: New status value (e.g., "AC", "WA", "TLE")

    Returns:
        Previous status if successful, None if no header found

    Examples:
        >>> old_status = update_problem_status("A.cpp", "AC")
        >>> print(old_status)
        ~
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        pattern = r'(\* Status:\s*)([^\n]*)'
        match = re.search(pattern, content)
        if not match:
            return None

        old_status = match.group(2).strip()
        updated = re.sub(pattern, rf'\g<1>{new_status}', content)

        with open(filepath, 'w') as f:
            f.write(updated)

        return old_status
    except Exception:
        return None


def find_samples(directory, problem):
    """
    Find sample test files (problem_1.in, problem_2.in, etc.).
    Handles gaps in numbering.

    Args:
        directory: Directory to search in
        problem: Problem identifier (e.g., "A", "1234B")

    Returns:
        List of dicts: [{'in': path, 'out': path | None, 'num': int}, ...]
        Sorted by test number

    Examples:
        >>> samples = find_samples("/contest", "A")
        >>> print(samples[0])
        {'in': '/contest/A_1.in', 'out': '/contest/A_1.out', 'num': 1}
    """
    pattern = re.compile(rf'^{re.escape(problem)}_(\d+)\.in$')
    samples = []

    for f in os.listdir(directory):
        m = pattern.match(f)
        if m:
            num = int(m.group(1))
            in_file = os.path.join(directory, f)
            out_file = os.path.join(directory, f"{problem}_{num}.out")
            samples.append({
                'in': in_file,
                'out': out_file if os.path.exists(out_file) else None,
                'num': num,
            })

    samples.sort(key=lambda s: s['num'])
    return samples


def save_samples(directory, problem, samples):
    """
    Save samples as problem_1.in/out, problem_2.in/out, etc.

    Args:
        directory: Directory to save in
        problem: Problem identifier
        samples: List of {'input': str, 'output': str} dicts

    Returns:
        Number of samples saved

    Examples:
        >>> samples = [{'input': '5\\n', 'output': '10\\n'}]
        >>> count = save_samples("/contest", "A", samples)
        >>> print(count)
        1
    """
    saved = 0
    for i, sample in enumerate(samples, 1):
        in_path = os.path.join(directory, f"{problem}_{i}.in")
        out_path = os.path.join(directory, f"{problem}_{i}.out")

        with open(in_path, 'w') as f:
            f.write(sample['input'] + '\n')

        if sample.get('output'):
            with open(out_path, 'w') as f:
                f.write(sample['output'] + '\n')

        saved += 1
    return saved


def next_test_index(directory, problem):
    """
    Find the next available test index.

    Args:
        directory: Directory to check
        problem: Problem identifier

    Returns:
        Next available index (e.g., if A_1.in and A_2.in exist, returns 3)

    Examples:
        >>> idx = next_test_index("/contest", "A")
        >>> print(idx)
        3
    """
    samples = find_samples(directory, problem)
    if not samples:
        return 1
    return samples[-1]['num'] + 1


def create_problem_file(filepath, template_path, header):
    """
    Create a new problem file from template with header.

    Args:
        filepath: Path for new .cpp file
        template_path: Path to template.cpp
        header: Header string (from generate_header())

    Returns:
        None

    Raises:
        FileNotFoundError: If template doesn't exist
    """
    with open(template_path, 'r') as f:
        template_body = f.read()

    with open(filepath, 'w') as f:
        f.write(header)
        f.write(template_body)


def find_file_case_insensitive(directory, target):
    """
    Find file with case-insensitive matching.

    Args:
        directory: Directory to search in
        target: Target filename (without extension)

    Returns:
        Full path if found, None otherwise

    Examples:
        >>> path = find_file_case_insensitive("/contest", "a")
        >>> print(path)
        /contest/A.cpp
    """
    if not os.path.isdir(directory):
        return None

    target_lower = target.lower()
    if target_lower.endswith('.cpp'):
        target_cpp = target
    else:
        target_cpp = f"{target}.cpp"
    target_cpp_lower = target_cpp.lower()

    for filename in os.listdir(directory):
        if filename.lower() == target_cpp_lower:
            return os.path.join(directory, filename)

    return None


def get_platform_dirs():
    """
    Get list of top-level platform directories for walking/scanning.

    This returns only the main platform directories (not subdirectories)
    used by commands like clean, commit, and update that walk the repository.

    Returns:
        List of top-level platform directory names
    """
    from lib.judges import ALL_JUDGES
    platform_names = [judge.platform_name for judge in ALL_JUDGES]
    return platform_names + ['Trainings', 'Other']


# For backwards compatibility, keep PLATFORM_DIRS as a dynamic call
# Commands that need subdirectories should import get_platform_directories from lib.judges
PLATFORM_DIRS = get_platform_dirs()

SAFE_FILES = {'LICENSE', 'Makefile', 'CNAME', 'README'}

BUILD_EXTENSIONS = {'.out', '.o', '.in', '.hashed'}


def get_repo_root():
    """Find the git root of the current working directory."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return os.getcwd()


def is_removable(filepath):
    """Check if a file is a compiled binary or build artifact."""
    name = os.path.basename(filepath)

    if name.startswith('_') or name.startswith('.'):
        return False

    if name in SAFE_FILES:
        return False

    _, ext = os.path.splitext(name)

    # Build artifacts and test files by extension
    if ext in BUILD_EXTENSIONS:
        return True

    # Extensionless binary detection
    if ext != '':
        return False

    try:
        with open(filepath, 'rb') as f:
            header = f.read(2)
            if header == b'#!':
                return False
    except (IOError, OSError):
        pass

    return True
