"""
Integration tests for commands/update.py
"""
import os
from unittest.mock import patch
from cptools.commands import update

def test_update_single_directory(tmp_path):
    """Test updating info.md in a single directory."""
    d = str(tmp_path)
    
    # Create dummy problem files
    # A.cpp is AC
    with open(os.path.join(d, "A.cpp"), 'w') as f:
        f.write("/**\n * Problem: A\n * Status: AC\n * Link: http://cf/A\n */")
    
    # B.cpp is WA
    with open(os.path.join(d, "B.cpp"), 'w') as f:
        f.write("/**\n * Problem: B\n * Status: WA\n */")

    # C.cpp is Pending (~)
    with open(os.path.join(d, "C.cpp"), 'w') as f:
        f.write("/**\n * Problem: C\n * Status: ~\n */")

    with patch('sys.argv', ['cptools-update', d]):
        update.run()

    info_md = os.path.join(d, "info.md")
    assert os.path.exists(info_md)
    
    with open(info_md, 'r') as f:
        content = f.read()
        # Check for emojis/status
        assert "✅" in content  # AC
        assert "⚠️" in content  # WA
        assert "⬜" in content  # Pending
        
        # Check progress summary
        assert "1/3 solved" in content
        
        # Check link generation
        assert "[A](http://cf/A)" in content
        assert "| B |" in content  # No link for B

def test_update_all(tmp_path):
    """Test updating all directories recursively."""
    root = str(tmp_path)
    
    # Create structure: Codeforces/123
    cf_dir = os.path.join(root, "Codeforces", "123")
    os.makedirs(cf_dir)
    with open(os.path.join(cf_dir, "A.cpp"), 'w') as f:
        f.write("/**\n * Problem: A\n * Status: AC\n */")

    # Patch ROOT_DIR since it's a global in the module initialized at import time
    # Patch PLATFORM_DIRS to only look at our mock Codeforces dir
    with patch('cptools.commands.update.ROOT_DIR', root), \
         patch('cptools.commands.update.PLATFORM_DIRS', ['Codeforces']), \
         patch('sys.argv', ['cptools-update', '--all']):
        
        update.run()

    assert os.path.exists(os.path.join(cf_dir, "info.md"))

def test_update_contest_format(tmp_path):
    """Test that contest directories generate info.md with contest metadata."""
    # Create a contest directory (Codeforces/123)
    contest_dir = tmp_path / "Codeforces" / "123"
    contest_dir.mkdir(parents=True)

    # Create problem with contest link
    problem_file = contest_dir / "A.cpp"
    problem_file.write_text(
        "/**\n"
        " * Problem: Test Problem A\n"
        " * Status: AC\n"
        " * Link: https://codeforces.com/contest/123/problem/A\n"
        " * Created: 01-01-2024 12:00:00\n"
        " */"
    )

    with patch('sys.argv', ['cptools-update', str(contest_dir)]):
        update.run()

    info_md = contest_dir / "info.md"
    assert info_md.exists()

    content = info_md.read_text()

    # Contest format should have:
    # 1. Contest link
    assert "**Contest**:" in content
    assert "https://codeforces.com/contest/123" in content

    # 2. Created date
    assert "**Created**:" in content
    assert "01-01-2024 12:00:00" in content

    # 3. Progress
    assert "**Progress**: 1/1 solved" in content

def test_update_problemset_format(tmp_path):
    """Test that problemset directories generate info.md without contest metadata."""
    # Create a problemset directory (CSES)
    problemset_dir = tmp_path / "CSES" / "dynamic_programming"
    problemset_dir.mkdir(parents=True)

    # Create problems
    for i, (problem_id, status) in enumerate([("1636", "AC"), ("1158", "~")]):
        problem_file = problemset_dir / f"{problem_id}.cpp"
        problem_file.write_text(
            f"/**\n"
            f" * Problem: Coin Combinations {i+1}\n"
            f" * Status: {status}\n"
            f" * Link: https://cses.fi/problemset/task/{problem_id}\n"
            f" * Created: 01-01-2024 12:00:00\n"
            f" */"
        )

    # Mock detect_platform_from_path to return CSES
    with patch('sys.argv', ['cptools-update', str(problemset_dir)]), \
         patch('cptools.commands.update.detect_platform_from_path', return_value=('CSES', 'dynamic_programming')):
        update.run()

    info_md = problemset_dir / "info.md"
    assert info_md.exists()

    content = info_md.read_text()

    # Problemset format should NOT have:
    # 1. Contest link
    assert "**Contest**:" not in content

    # 2. Created date
    assert "**Created**:" not in content

    # Problemset format SHOULD have:
    # 3. Progress
    assert "**Progress**: 1/2 solved" in content

    # 4. Individual problem links
    assert "https://cses.fi/problemset/task/1636" in content
    assert "https://cses.fi/problemset/task/1158" in content

def test_update_codeforces_problemset_format(tmp_path):
    """Test that Codeforces/Problemset directories are treated as problemsets."""
    # Create Codeforces Problemset directory
    problemset_dir = tmp_path / "Codeforces" / "Problemset" / "dp"
    problemset_dir.mkdir(parents=True)

    # Create problem
    problem_file = problemset_dir / "1234A.cpp"
    problem_file.write_text(
        "/**\n"
        " * Problem: DP Problem\n"
        " * Status: AC\n"
        " * Link: https://codeforces.com/problemset/problem/1234/A\n"
        " * Created: 01-01-2024 12:00:00\n"
        " */"
    )

    # Mock detect_platform_from_path to return Codeforces Problemset
    with patch('sys.argv', ['cptools-update', str(problemset_dir)]), \
         patch('cptools.commands.update.detect_platform_from_path', return_value=('Codeforces Problemset', 'dp')):
        update.run()

    info_md = problemset_dir / "info.md"
    assert info_md.exists()

    content = info_md.read_text()

    # Should be treated as problemset (no contest metadata)
    assert "**Contest**:" not in content
    assert "**Created**:" not in content
    assert "**Progress**: 1/1 solved" in content

def test_update_filters_problem_variations(tmp_path):
    """Test that problem variations (files with -suffix) are filtered correctly."""
    d = tmp_path / "SPOJ"
    d.mkdir()

    # Create base problem with header
    (d / "COT.cpp").write_text(
        "/**\n"
        " * Problem: Count on a Tree\n"
        " * Status: AC\n"
        " * Link: https://www.spoj.com/problems/COT/\n"
        " */"
    )

    # Create variation with suffix (should be ignored)
    (d / "COT-compressed.cpp").write_text(
        "/**\n"
        " * Problem: Count on a Tree (Compressed)\n"
        " * Status: AC\n"
        " * Link: https://www.spoj.com/problems/COT/\n"
        " */"
    )

    # Create another base problem
    (d / "MKTHNUM.cpp").write_text(
        "/**\n"
        " * Problem: K-th Number\n"
        " * Status: WA\n"
        " * Link: https://www.spoj.com/problems/MKTHNUM/\n"
        " */"
    )

    with patch('sys.argv', ['cptools-update', str(d)]):
        update.run()

    info_md = d / "info.md"
    assert info_md.exists()

    content = info_md.read_text()

    # Should only have 2 problems (COT and MKTHNUM)
    assert "**Progress**: 1/2 solved" in content

    # Should include base COT problem
    assert "Count on a Tree" in content
    assert "[Count on a Tree](https://www.spoj.com/problems/COT/)" in content

    # Should NOT include compressed variation
    assert "Compressed" not in content

    # Should include MKTHNUM
    assert "K-th Number" in content

def test_update_variations_without_base(tmp_path):
    """Test that when no base version exists, first variation is used."""
    d = tmp_path / "contest"
    d.mkdir()

    # Create only variations (no base A.cpp)
    (d / "A-v1.cpp").write_text(
        "/**\n"
        " * Problem: Problem A Version 1\n"
        " * Status: AC\n"
        " */"
    )

    (d / "A-v2.cpp").write_text(
        "/**\n"
        " * Problem: Problem A Version 2\n"
        " * Status: AC\n"
        " */"
    )

    with patch('sys.argv', ['cptools-update', str(d)]):
        update.run()

    info_md = d / "info.md"
    assert info_md.exists()

    content = info_md.read_text()

    # Should only have 1 problem
    assert "**Progress**: 1/1 solved" in content

    # Should use first variation alphabetically (A-v1)
    assert "Problem A Version 1" in content

    # Should NOT include v2
    assert "Version 2" not in content

def test_update_multiple_variations_prefers_base(tmp_path):
    """Test that base version is preferred over multiple variations."""
    d = tmp_path / "contest"
    d.mkdir()

    # Create base version
    (d / "B.cpp").write_text(
        "/**\n"
        " * Problem: Problem B Base\n"
        " * Status: AC\n"
        " */"
    )

    # Create multiple variations
    (d / "B-optimized.cpp").write_text(
        "/**\n"
        " * Problem: Problem B Optimized\n"
        " * Status: AC\n"
        " */"
    )

    (d / "B-alternative.cpp").write_text(
        "/**\n"
        " * Problem: Problem B Alternative\n"
        " * Status: AC\n"
        " */"
    )

    with patch('sys.argv', ['cptools-update', str(d)]):
        update.run()

    info_md = d / "info.md"
    assert info_md.exists()

    content = info_md.read_text()

    # Should only have 1 problem
    assert "**Progress**: 1/1 solved" in content

    # Should use base version
    assert "Problem B Base" in content

    # Should NOT include variations
    assert "Optimized" not in content
    assert "Alternative" not in content