"""
Tests for lib/fileops.py - File operations and header management.
"""
import os
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open
from lib.fileops import (
    generate_header,
    read_problem_header,
    update_problem_status,
    find_samples,
    save_samples,
    next_test_index,
    create_problem_file,
    find_file_case_insensitive,
    get_repo_root,
    is_removable,
)


def test_generate_header():
    """Test generating C++ file header."""
    dt = datetime(2024, 1, 1, 12, 0, 0)
    header = generate_header(
        problem_id="A",
        link="http://example.com",
        problem_name="Test Problem",
        author="Tester",
        status="AC",
        created=dt
    )
    
    assert "Author:      Tester" in header
    assert "Problem:     A - Test Problem" in header
    assert "Link:        http://example.com" in header
    assert "Status:      AC" in header
    assert "Created:     01-01-2024 12:00:00" in header


def test_read_problem_header(sample_cpp_file):
    """Test reading header from existing file."""
    header = read_problem_header(sample_cpp_file)
    assert header is not None
    assert header.problem == "A - Test Problem"
    assert header.link == "https://codeforces.com/contest/1234/problem/A"
    assert header.status == "~"
    assert header.created == "01-01-2024 12:00:00"


def test_update_problem_status(sample_cpp_file):
    """Test updating status in file header."""
    old_status = update_problem_status(sample_cpp_file, "AC")
    assert old_status == "~"
    
    header = read_problem_header(sample_cpp_file)
    assert header is not None
    assert header.status == "AC"


def test_save_and_find_samples(temp_dir):
    """Test saving and finding sample files."""
    samples = [
        {'input': '1\n', 'output': '2\n'},
        {'input': '3\n', 'output': '6\n'}
    ]
    
    # Save samples
    count = save_samples(temp_dir, "B", samples)
    assert count == 2
    
    assert os.path.exists(os.path.join(temp_dir, "B_1.in"))
    assert os.path.exists(os.path.join(temp_dir, "B_1.out"))
    assert os.path.exists(os.path.join(temp_dir, "B_2.in"))
    
    # Find samples
    found = find_samples(temp_dir, "B")
    assert len(found) == 2
    assert found[0]['num'] == 1
    assert found[0]['in'].endswith("B_1.in")
    assert found[1]['num'] == 2


def test_next_test_index(temp_dir):
    """Test calculating next test index."""
    # No samples yet
    assert next_test_index(temp_dir, "C") == 1
    
    # Add C_1.in
    with open(os.path.join(temp_dir, "C_1.in"), 'w') as f: f.write("")
    assert next_test_index(temp_dir, "C") == 2
    
    # Add C_2.in
    with open(os.path.join(temp_dir, "C_2.in"), 'w') as f: f.write("")
    assert next_test_index(temp_dir, "C") == 3


def test_create_problem_file(temp_dir, sample_template):
    """Test creating a new problem file from template."""
    template_path = os.path.join(temp_dir, "template.cpp")
    with open(template_path, 'w') as f:
        f.write(sample_template)
        
    dest_path = os.path.join(temp_dir, "New.cpp")
    header = "// Header\n"
    
    create_problem_file(dest_path, template_path, header)
    
    with open(dest_path, 'r') as f:
        content = f.read()
        assert content.startswith("// Header\n")
        assert "int main()" in content


def test_find_file_case_insensitive(temp_dir):
    """Test finding files ignoring case."""
    with open(os.path.join(temp_dir, "ProblemA.cpp"), 'w') as f: f.write("")
    
    assert find_file_case_insensitive(temp_dir, "problema") == os.path.join(temp_dir, "ProblemA.cpp")
    assert find_file_case_insensitive(temp_dir, "ProblemA") == os.path.join(temp_dir, "ProblemA.cpp")
    assert find_file_case_insensitive(temp_dir, "NonExistent") is None


def test_get_repo_root():
    """Test finding git repo root."""
    with patch('subprocess.run') as mock_run:
        # Case 1: Git success
        mock_run.return_value = MagicMock(returncode=0, stdout="/path/to/repo\n")
        assert get_repo_root() == "/path/to/repo"

        # Case 2: Git failure (not a repo)
        mock_run.return_value = MagicMock(returncode=1)
        # Should fallback to cwd
        assert get_repo_root() == os.getcwd()


def test_is_removable():
    """Test file removability logic."""
    # Should remove:
    assert is_removable("test.out")
    assert is_removable("test.o")
    assert is_removable("test.in")
    assert is_removable("test.hashed")
    assert is_removable("binary_file")  # No extension

    # Should NOT remove:
    assert not is_removable("test.cpp")
    assert not is_removable("Makefile")
    assert not is_removable("README")
    assert not is_removable(".git")
    assert not is_removable("_ignore")

    # Test binary detection (shebang check)
    with patch("builtins.open", mock_open(read_data=b"#!/bin/bash")) as mock_file:
        # Script with shebang should NOT be removed
        assert not is_removable("script")

    with patch("builtins.open", mock_open(read_data=b"\x7fELF")) as mock_file:
        # Binary ELF should be removed (default fallthrough for no extension)
        assert is_removable("binary")

    # Test error handling in open
    with patch("builtins.open") as mock_file:
        mock_file.side_effect = OSError
        # If can't open, assumes removable if no extension?
        # Logic says: try open, if error pass, return True.
        assert is_removable("locked_file")