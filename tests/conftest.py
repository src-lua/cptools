"""
Pytest fixtures for cptools tests.

This file defines reusable test setup functions (fixtures) that can be
used by any test in the `tests/` directory.
"""
import pytest
import os
import tempfile
import shutil

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests to run in."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

@pytest.fixture
def sample_cpp_file(temp_dir):
    """Create a sample C++ file with a header."""
    content = \
"""/**
 * Author:      Tester
 * Problem:     A - Test Problem
 * Link:        https://codeforces.com/contest/1234/problem/A
 * Status:      ~
 * Created:     01-01-2024 12:00:00
 **/
int main() {}
"""
    filepath = os.path.join(temp_dir, "A.cpp")
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath

@pytest.fixture
def sample_template():
    """Provide a minimal C++ template content."""
    return "int main() {\n    return 0;\n}\n"