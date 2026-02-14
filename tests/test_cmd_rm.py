"""
Integration tests for commands/rm.py
"""
import os
import sys
from unittest.mock import patch
from commands import rm

def test_remove_problem(tmp_path):
    """Test removing problem files and associated artifacts."""
    temp_dir = str(tmp_path)

    # Create dummy files simulating a problem environment
    files = ["A.cpp", "A_1.in", "A_1.out", "A"]
    for f in files:
        with open(os.path.join(temp_dir, f), 'w') as handle:
            handle.write("data")

    # Ensure they exist before removal
    for f in files:
        assert os.path.exists(os.path.join(temp_dir, f))

    # Run remove
    assert rm.remove_problem("A", temp_dir)

    # Ensure they are gone
    for f in files:
        assert not os.path.exists(os.path.join(temp_dir, f))


def test_remove_nonexistent(tmp_path):
    """Test removing nonexistent problem returns False."""
    temp_dir = str(tmp_path)
    assert not rm.remove_problem("Z", temp_dir)


def test_remove_multiple_problems(tmp_path):
    """Test removing multiple problems at once."""
    temp_dir = str(tmp_path)

    # Create files for problems A and B
    for prob in ["A", "B"]:
        with open(os.path.join(temp_dir, f"{prob}.cpp"), 'w') as f:
            f.write("code")
        with open(os.path.join(temp_dir, f"{prob}_1.in"), 'w') as f:
            f.write("input")

    with patch.object(sys, 'argv', ['cptools-rm', 'A', 'B', temp_dir]):
        rm.run()

    # Both should be removed
    assert not os.path.exists(os.path.join(temp_dir, "A.cpp"))
    assert not os.path.exists(os.path.join(temp_dir, "B.cpp"))


def test_remove_preserves_other_files(tmp_path):
    """Test that non-problem files are preserved."""
    temp_dir = str(tmp_path)

    with open(os.path.join(temp_dir, "C.cpp"), 'w') as f:
        f.write("code")
    with open(os.path.join(temp_dir, "C.hashed"), 'w') as f:
        f.write("hashes")
    with open(os.path.join(temp_dir, "README.md"), 'w') as f:
        f.write("readme")

    rm.remove_problem("C", temp_dir)

    assert not os.path.exists(os.path.join(temp_dir, "C.cpp"))
    # .hashed files ARE removed by rm command (Q21)
    assert not os.path.exists(os.path.join(temp_dir, "C.hashed"))
    # Unrelated files are preserved
    assert os.path.exists(os.path.join(temp_dir, "README.md"))


def test_remove_main_current_directory(tmp_path, monkeypatch):
    """Test main function using current directory."""
    monkeypatch.chdir(tmp_path)

    with open(tmp_path / "D.cpp", 'w') as f:
        f.write("code")

    with patch.object(sys, 'argv', ['cptools-rm', 'D']):
        rm.run()

    assert not os.path.exists(tmp_path / "D.cpp")


def test_remove_problem_without_samples(tmp_path):
    """Test removing problem with no sample files."""
    temp_dir = str(tmp_path)

    # Only create .cpp file
    with open(os.path.join(temp_dir, "E.cpp"), 'w') as f:
        f.write("code")

    assert rm.remove_problem("E", temp_dir)
    assert not os.path.exists(os.path.join(temp_dir, "E.cpp"))


def test_remove_problem_with_many_samples(tmp_path):
    """Test removing problem with multiple sample files."""
    temp_dir = str(tmp_path)

    with open(os.path.join(temp_dir, "F.cpp"), 'w') as f:
        f.write("code")

    # Create 5 sample pairs
    for i in range(1, 6):
        with open(os.path.join(temp_dir, f"F_{i}.in"), 'w') as f:
            f.write(f"input {i}")
        with open(os.path.join(temp_dir, f"F_{i}.out"), 'w') as f:
            f.write(f"output {i}")

    rm.remove_problem("F", temp_dir)

    assert not os.path.exists(os.path.join(temp_dir, "F.cpp"))
    for i in range(1, 6):
        assert not os.path.exists(os.path.join(temp_dir, f"F_{i}.in"))
        assert not os.path.exists(os.path.join(temp_dir, f"F_{i}.out"))


def test_remove_preserves_hidden_files(tmp_path):
    """Test that hidden files are preserved."""
    temp_dir = str(tmp_path)

    with open(os.path.join(temp_dir, "G.cpp"), 'w') as f:
        f.write("code")
    with open(os.path.join(temp_dir, ".G"), 'w') as f:
        f.write("hidden binary")

    rm.remove_problem("G", temp_dir)

    assert not os.path.exists(os.path.join(temp_dir, "G.cpp"))
    # Hidden binary files are NOT removed by rm command
    assert os.path.exists(os.path.join(temp_dir, ".G"))


def test_remove_hashed_files(tmp_path):
    """Test that .hashed files are removed (Q21 fix)."""
    temp_dir = str(tmp_path)

    # Create problem file and its .hashed file
    with open(os.path.join(temp_dir, "H.cpp"), 'w') as f:
        f.write("code")
    with open(os.path.join(temp_dir, "H.hashed"), 'w') as f:
        f.write("abc line1\ndef line2\n")

    # Verify both exist before removal
    assert os.path.exists(os.path.join(temp_dir, "H.cpp"))
    assert os.path.exists(os.path.join(temp_dir, "H.hashed"))

    # Remove problem
    rm.remove_problem("H", temp_dir)

    # Both should be removed
    assert not os.path.exists(os.path.join(temp_dir, "H.cpp"))
    assert not os.path.exists(os.path.join(temp_dir, "H.hashed"))


def test_remove_problem_with_all_artifacts(tmp_path):
    """Test removing problem with all possible artifacts (Q21)."""
    temp_dir = str(tmp_path)

    # Create all types of files
    files_to_create = {
        "I.cpp": "code",
        "I": "binary",
        "I.hashed": "hashes",
        "I_1.in": "input 1",
        "I_1.out": "output 1",
        "I_2.in": "input 2",
        "I_2.out": "output 2",
    }

    for filename, content in files_to_create.items():
        with open(os.path.join(temp_dir, filename), 'w') as f:
            f.write(content)

    # Verify all exist
    for filename in files_to_create:
        assert os.path.exists(os.path.join(temp_dir, filename))

    # Remove problem
    rm.remove_problem("I", temp_dir)

    # All should be removed
    for filename in files_to_create:
        assert not os.path.exists(os.path.join(temp_dir, filename))


def test_remove_last_file_removes_info_md(tmp_path):
    """Test that info.md is removed when last .cpp file is removed."""
    temp_dir = str(tmp_path)

    # Create a problem file
    with open(os.path.join(temp_dir, "A.cpp"), 'w') as f:
        f.write("code")

    # Create info.md
    with open(os.path.join(temp_dir, "info.md"), 'w') as f:
        f.write("# Contest Info\n")

    # Verify both exist
    assert os.path.exists(os.path.join(temp_dir, "A.cpp"))
    assert os.path.exists(os.path.join(temp_dir, "info.md"))

    # Remove the last problem
    with patch('sys.argv', ['cptools-rm', 'A', temp_dir]):
        rm.run()

    # Both should be removed
    assert not os.path.exists(os.path.join(temp_dir, "A.cpp"))
    assert not os.path.exists(os.path.join(temp_dir, "info.md"))


def test_remove_with_cpp_extension(tmp_path):
    """Test removing problem using filename with .cpp extension."""
    temp_dir = str(tmp_path)

    # Create dummy files
    files = ["KQUERY.cpp", "KQUERY_1.in", "KQUERY_1.out"]
    for f in files:
        with open(os.path.join(temp_dir, f), 'w') as handle:
            handle.write("data")

    # Ensure they exist before removal
    for f in files:
        assert os.path.exists(os.path.join(temp_dir, f))

    # Run remove with .cpp extension
    with patch.object(sys, 'argv', ['cptools-rm', 'KQUERY.cpp', temp_dir]):
        rm.run()

    # Ensure they are gone
    for f in files:
        assert not os.path.exists(os.path.join(temp_dir, f))


def test_remove_range_basic(tmp_path):
    """Test removing a range of problems (Q20)."""
    temp_dir = str(tmp_path)

    # Create problems A, B, C
    for letter in ['A', 'B', 'C']:
        with open(os.path.join(temp_dir, f"{letter}.cpp"), 'w') as f:
            f.write("code")

    # Remove A~C
    with patch.object(sys, 'argv', ['cptools-rm', 'A~C', temp_dir]):
        rm.run()

    # All should be removed
    assert not os.path.exists(os.path.join(temp_dir, "A.cpp"))
    assert not os.path.exists(os.path.join(temp_dir, "B.cpp"))
    assert not os.path.exists(os.path.join(temp_dir, "C.cpp"))


def test_remove_range_with_samples(tmp_path):
    """Test removing range also removes sample files (Q20)."""
    temp_dir = str(tmp_path)

    # Create problems A and B with samples
    for letter in ['A', 'B']:
        with open(os.path.join(temp_dir, f"{letter}.cpp"), 'w') as f:
            f.write("code")
        with open(os.path.join(temp_dir, f"{letter}_1.in"), 'w') as f:
            f.write("input")
        with open(os.path.join(temp_dir, f"{letter}_1.out"), 'w') as f:
            f.write("output")

    # Remove A~B
    with patch.object(sys, 'argv', ['cptools-rm', 'A~B', temp_dir]):
        rm.run()

    # All files should be removed
    for letter in ['A', 'B']:
        assert not os.path.exists(os.path.join(temp_dir, f"{letter}.cpp"))
        assert not os.path.exists(os.path.join(temp_dir, f"{letter}_1.in"))
        assert not os.path.exists(os.path.join(temp_dir, f"{letter}_1.out"))


def test_remove_large_range_with_confirmation(tmp_path):
    """Test removing large range (>3 problems) requires confirmation (Q20)."""
    temp_dir = str(tmp_path)

    # Create problems A through E (5 problems)
    for letter in ['A', 'B', 'C', 'D', 'E']:
        with open(os.path.join(temp_dir, f"{letter}.cpp"), 'w') as f:
            f.write("code")

    # User cancels the operation
    with patch.object(sys, 'argv', ['cptools-rm', 'A~E', temp_dir]):
        with patch('builtins.input', return_value='n'):
            rm.run()

    # All files should still exist
    for letter in ['A', 'B', 'C', 'D', 'E']:
        assert os.path.exists(os.path.join(temp_dir, f"{letter}.cpp"))

    # User confirms the operation
    with patch.object(sys, 'argv', ['cptools-rm', 'A~E', temp_dir]):
        with patch('builtins.input', return_value='y'):
            rm.run()

    # All files should be removed
    for letter in ['A', 'B', 'C', 'D', 'E']:
        assert not os.path.exists(os.path.join(temp_dir, f"{letter}.cpp"))


def test_remove_range_with_individual_problems(tmp_path):
    """Test mixing range and individual problems (Q20)."""
    temp_dir = str(tmp_path)

    # Create problems A, B, C, E, F
    for letter in ['A', 'B', 'C', 'E', 'F']:
        with open(os.path.join(temp_dir, f"{letter}.cpp"), 'w') as f:
            f.write("code")

    # Remove A~B and F
    with patch.object(sys, 'argv', ['cptools-rm', 'A~B', 'F', temp_dir]):
        rm.run()

    # A, B, F should be removed
    assert not os.path.exists(os.path.join(temp_dir, "A.cpp"))
    assert not os.path.exists(os.path.join(temp_dir, "B.cpp"))
    assert not os.path.exists(os.path.join(temp_dir, "F.cpp"))

    # C, E should still exist
    assert os.path.exists(os.path.join(temp_dir, "C.cpp"))
    assert os.path.exists(os.path.join(temp_dir, "E.cpp"))


def test_remove_range_with_duplicates(tmp_path):
    """Test removing range handles duplicates correctly (Q20)."""
    temp_dir = str(tmp_path)

    # Create problems A, B
    for letter in ['A', 'B']:
        with open(os.path.join(temp_dir, f"{letter}.cpp"), 'w') as f:
            f.write("code")

    # Remove A~B A (duplicate specification)
    with patch.object(sys, 'argv', ['cptools-rm', 'A~B', 'A', temp_dir]):
        rm.run()

    # Both should be removed (no errors from duplicate)
    assert not os.path.exists(os.path.join(temp_dir, "A.cpp"))
    assert not os.path.exists(os.path.join(temp_dir, "B.cpp"))


def test_remove_range_with_cpp_extension(tmp_path):
    """Test removing range works with .cpp extensions (Q20)."""
    temp_dir = str(tmp_path)

    # Create problems A, B, C
    for letter in ['A', 'B', 'C']:
        with open(os.path.join(temp_dir, f"{letter}.cpp"), 'w') as f:
            f.write("code")

    # Remove A.cpp~C.cpp (should strip extensions)
    with patch.object(sys, 'argv', ['cptools-rm', 'A.cpp~C.cpp', temp_dir]):
        rm.run()

    # All should be removed
    assert not os.path.exists(os.path.join(temp_dir, "A.cpp"))
    assert not os.path.exists(os.path.join(temp_dir, "B.cpp"))
    assert not os.path.exists(os.path.join(temp_dir, "C.cpp"))
