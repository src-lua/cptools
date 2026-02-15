"""
Integration tests for commands/clean.py
"""
import os
import sys
from unittest.mock import patch
from cptools.commands import clean
import pytest

def test_clean_directory(tmp_path):
    """Test cleaning build artifacts."""
    d = tmp_path

    # Create files
    (d / "main.cpp").write_text("code")
    (d / "main.out").write_text("binary")
    (d / "main.o").write_text("object")
    (d / "input.in").write_text("input")
    (d / "README").write_text("readme")

    # Run clean
    clean.clean_directory(str(d))

    # Verify
    assert (d / "main.cpp").exists()
    assert (d / "README").exists()
    assert not (d / "main.out").exists()
    assert not (d / "main.o").exists()
    assert not (d / "input.in").exists()


def test_clean_recursive(tmp_path):
    """Test recursive cleaning."""
    d = tmp_path
    sub = d / "subdir"
    sub.mkdir()

    (d / "root.out").write_text("bin")
    (sub / "sub.out").write_text("bin")

    clean.clean_directory(str(d), recursive=True)

    assert not (d / "root.out").exists()
    assert not (sub / "sub.out").exists()


def test_clean_main_with_all_flag(tmp_path):
    """Test main with --all flag."""
    with patch('cptools.commands.clean.ROOT_DIR', str(tmp_path)), \
         patch('cptools.commands.clean.PLATFORM_DIRS', ['Codeforces', 'AtCoder']), \
         patch.object(sys, 'argv', ['cptools-clean', '--all']):

        # Create platform directories with artifacts
        cf_dir = tmp_path / "Codeforces"
        cf_dir.mkdir()
        (cf_dir / "test.out").write_text("binary")

        at_dir = tmp_path / "AtCoder"
        at_dir.mkdir()
        (at_dir / "test.o").write_text("object")

        clean.run()

        assert not (cf_dir / "test.out").exists()
        assert not (at_dir / "test.o").exists()


def test_clean_main_single_directory(tmp_path):
    """Test main with single directory."""
    d = tmp_path
    (d / "test.out").write_text("binary")

    with patch.object(sys, 'argv', ['cptools-clean', str(d)]):
        clean.run()

        assert not (d / "test.out").exists()


def test_clean_main_invalid_directory():
    """Test error when directory doesn't exist."""
    with patch.object(sys, 'argv', ['cptools-clean', '/nonexistent/path']):
        with pytest.raises(SystemExit) as exc_info:
            clean.run()
        assert exc_info.value.code == 1


def test_clean_skips_dotfiles(tmp_path):
    """Test that hidden directories are skipped in recursive mode."""
    d = tmp_path
    hidden = d / ".hidden"
    hidden.mkdir()
    (hidden / "file.out").write_text("binary")

    clean.clean_directory(str(d), recursive=True)

    # Hidden directory and its contents should be preserved
    assert (hidden / "file.out").exists()


def test_clean_returns_count(tmp_path):
    """Test that clean_directory returns correct count of removed files."""
    d = tmp_path
    (d / "a.out").write_text("")
    (d / "b.out").write_text("")
    (d / "c.o").write_text("")

    count = clean.clean_directory(str(d))

    assert count == 3


def test_clean_handles_permission_error(tmp_path):
    """Test handling of files that can't be deleted."""
    d = tmp_path
    file = d / "locked.out"
    file.write_text("data")

    # Mock os.remove to raise OSError
    original_remove = os.remove

    def mock_remove(path):
        if "locked.out" in path:
            raise OSError("Permission denied")
        return original_remove(path)

    with patch('os.remove', side_effect=mock_remove):
        count = clean.clean_directory(str(d))

    # Should not remove the file but should not crash
    assert count == 0
    assert file.exists()
