"""
Integration tests for commands/mark.py
"""
import os
from unittest.mock import patch
from commands import mark
from lib.fileops import read_problem_header

def test_mark_updates_status(tmp_path):
    """Test marking a problem updates its status."""
    d = str(tmp_path)
    p = os.path.join(d, "A.cpp")
    with open(p, 'w') as f:
        f.write("/**\n * Problem: A\n * Status: ~\n */")
        
    with patch('sys.argv', ['cptools-mark', 'A', 'AC', d]):
        mark.run()
        
    header = read_problem_header(p)
    assert header.status == "AC"

def test_mark_range(tmp_path):
    """Test marking a range of problems."""
    d = str(tmp_path)
    for name in ["A.cpp", "B.cpp"]:
        with open(os.path.join(d, name), 'w') as f:
            f.write(f"/**\n * Problem: {name[0]}\n * Status: ~\n */")

    with patch('sys.argv', ['cptools-mark', 'A~B', 'WA', d]):
        mark.run()

    assert read_problem_header(os.path.join(d, "A.cpp")).status == "WA"
    assert read_problem_header(os.path.join(d, "B.cpp")).status == "WA"

def test_mark_lowercase_problem_id(tmp_path):
    """Test marking a problem with lowercase ID (Q16 fix)."""
    d = str(tmp_path)
    p = os.path.join(d, "abc123_a.cpp")
    with open(p, 'w') as f:
        f.write("/**\n * Problem: abc123_a\n * Status: ~\n */")

    with patch('sys.argv', ['cptools-mark', 'abc123_a', 'AC', d]):
        mark.run()

    header = read_problem_header(p)
    assert header.status == "AC"
    assert header.problem == "abc123_a"  # Verify case is preserved

def test_mark_mixed_case_problem_id(tmp_path):
    """Test marking a problem with mixed case ID (Q16 fix)."""
    d = str(tmp_path)
    p = os.path.join(d, "dp_Subset.cpp")
    with open(p, 'w') as f:
        f.write("/**\n * Problem: dp_Subset\n * Status: ~\n */")

    with patch('sys.argv', ['cptools-mark', 'dp_Subset', 'WIP', d]):
        mark.run()

    header = read_problem_header(p)
    assert header.status == "WIP"
    assert header.problem == "dp_Subset"  # Verify case is preserved

def test_mark_numeric_problem_id(tmp_path):
    """Test marking a problem with numeric ID (e.g., CSES problems)."""
    d = str(tmp_path)
    p = os.path.join(d, "1234.cpp")
    with open(p, 'w') as f:
        f.write("/**\n * Problem: 1234\n * Status: ~\n */")

    with patch('sys.argv', ['cptools-mark', '1234', 'AC', d]):
        mark.run()

    header = read_problem_header(p)
    assert header.status == "AC"
    assert header.problem == "1234"

def test_mark_with_cpp_extension(tmp_path):
    """Test marking a problem using filename with .cpp extension."""
    d = str(tmp_path)
    p = os.path.join(d, "KQUERY.cpp")
    with open(p, 'w') as f:
        f.write("/**\n * Problem: KQUERY\n * Status: ~\n */")

    # Should work when passing "KQUERY.cpp" instead of just "KQUERY"
    with patch('sys.argv', ['cptools-mark', 'KQUERY.cpp', 'AC', d]):
        mark.run()

    header = read_problem_header(p)
    assert header.status == "AC"
    assert header.problem == "KQUERY"


def test_mark_tilde_status_shell_expansion(tmp_path, monkeypatch):
    """Test marking with ~ status when shell expands it to home directory."""
    d = str(tmp_path)
    monkeypatch.chdir(d)

    p = os.path.join(d, "A.cpp")
    with open(p, 'w') as f:
        f.write("/**\n * Problem: A\n * Status: AC\n */")

    # Simulate shell expansion: when user types "cptools mark A ~",
    # the shell expands ~ to the home directory (e.g., /home/user)
    home_dir = os.path.expanduser('~')
    with patch('sys.argv', ['cptools-mark', 'A', home_dir]):
        mark.run()

    # Should interpret home_dir as the status '~', not as a directory
    header = read_problem_header(p)
    assert header.status == "~"