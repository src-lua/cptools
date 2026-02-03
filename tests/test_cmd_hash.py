"""
Integration tests for commands/hash.py
"""
import os
import sys
import subprocess
from unittest.mock import patch
from commands import hash as cmd_hash
import pytest

def test_hash_file_stdout(tmp_path, capsys):
    """Test hashing a file and printing to stdout."""
    f = tmp_path / "A.cpp"
    f.write_text("int main() {}")

    # Mock hasher compilation and execution
    with patch('commands.hash.get_or_compile_hasher', return_value='/mock/hasher'), \
         patch('subprocess.run') as mock_run:

        mock_run.return_value.stdout = "ABC int main() {}\n"
        mock_run.return_value.returncode = 0

        cmd_hash.hash_file(str(f), "A.cpp", save_to_file=False)

        mock_run.assert_called_once()
        captured = capsys.readouterr()
        assert "ABC int main() {}" in captured.out


def test_hash_file_save(tmp_path):
    """Test hashing a file and saving to .hashed file."""
    f = tmp_path / "A.cpp"
    f.write_text("int main() {}")

    with patch('commands.hash.get_or_compile_hasher', return_value='/mock/hasher'), \
         patch('subprocess.run') as mock_run:

        mock_run.return_value.stdout = "ABC int main() {}\n"
        mock_run.return_value.returncode = 0

        cmd_hash.hash_file(str(f), "A.cpp", save_to_file=True)

        hashed_file = tmp_path / "A.hashed"
        assert hashed_file.exists()
        assert hashed_file.read_text() == "ABC int main() {}\n"


def test_hash_file_not_found(tmp_path):
    """Test error when file doesn't exist."""
    with pytest.raises(SystemExit) as exc_info:
        cmd_hash.hash_file(str(tmp_path / "NonExistent.cpp"), "NonExistent.cpp")
    assert exc_info.value.code == 1


def test_hash_execution_error(tmp_path):
    """Test error when hasher execution fails."""
    f = tmp_path / "B.cpp"
    f.write_text("int main() {}")

    with patch('commands.hash.get_or_compile_hasher', return_value='/mock/hasher'), \
         patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'hasher', stderr="Error")):

        with pytest.raises(SystemExit) as exc_info:
            cmd_hash.hash_file(str(f), "B.cpp")
        assert exc_info.value.code == 1


def test_hash_temp_files_cleanup(tmp_path, monkeypatch):
    """Test that temporary files are cleaned up after hashing."""
    monkeypatch.chdir(tmp_path)

    f = tmp_path / "C.cpp"
    f.write_text("int main() {}")

    # Create temp files that should be cleaned
    (tmp_path / "z.cpp").write_text("temp")
    (tmp_path / "sh").write_text("temp")

    with patch('commands.hash.get_or_compile_hasher', return_value='/mock/hasher'), \
         patch('subprocess.run') as mock_run:

        mock_run.return_value.stdout = "XYZ int main() {}\n"
        mock_run.return_value.returncode = 0

        cmd_hash.hash_file(str(f), "C.cpp")

        # Verify temp files were cleaned
        assert not os.path.exists("z.cpp")
        assert not os.path.exists("sh")


def test_hash_main_with_save(tmp_path, monkeypatch):
    """Test main function with --save flag."""
    monkeypatch.chdir(tmp_path)

    f = tmp_path / "D.cpp"
    f.write_text("int main() { return 0; }")

    with patch.object(sys, 'argv', ['cptools-hash', 'D', '--save']), \
         patch('commands.hash.get_or_compile_hasher', return_value='/mock/hasher'), \
         patch('subprocess.run') as mock_run:

        mock_run.return_value.stdout = "123 int main() { return 0; }\n"
        mock_run.return_value.returncode = 0

        cmd_hash.run()

        assert os.path.exists("D.hashed")


def test_hash_main_without_save(tmp_path, monkeypatch, capsys):
    """Test main function without --save flag (stdout mode)."""
    monkeypatch.chdir(tmp_path)

    f = tmp_path / "E.cpp"
    f.write_text("#include <iostream>")

    with patch.object(sys, 'argv', ['cptools-hash', 'E']), \
         patch('commands.hash.get_or_compile_hasher', return_value='/mock/hasher'), \
         patch('subprocess.run') as mock_run:

        mock_run.return_value.stdout = "456 #include <iostream>\n"
        mock_run.return_value.returncode = 0

        cmd_hash.run()

        captured = capsys.readouterr()
        assert "456 #include <iostream>" in captured.out


def test_hash_with_cpp_extension(tmp_path, monkeypatch):
    """Test hashing with explicit .cpp extension in argument."""
    monkeypatch.chdir(tmp_path)

    f = tmp_path / "F.cpp"
    f.write_text("void foo() {}")

    with patch.object(sys, 'argv', ['cptools-hash', 'F.cpp']), \
         patch('commands.hash.get_or_compile_hasher', return_value='/mock/hasher'), \
         patch('subprocess.run') as mock_run:

        mock_run.return_value.stdout = "789 void foo() {}\n"
        mock_run.return_value.returncode = 0

        cmd_hash.run()

        mock_run.assert_called_once()


def test_get_or_compile_hasher_first_time(tmp_path):
    """Test compiling hasher for the first time."""
    with patch('os.path.expanduser', return_value=str(tmp_path)), \
         patch('subprocess.run') as mock_run:

        mock_run.return_value.returncode = 0

        hasher_path = cmd_hash.get_or_compile_hasher()

        # Should have compiled
        mock_run.assert_called_once()
        assert hasher_path.endswith("hasher")


def test_get_or_compile_hasher_already_exists(tmp_path):
    """Test using existing hasher binary."""
    # Setup cache directory structure
    home_dir = tmp_path
    cache_dir = home_dir / ".cache" / "cptools"
    cache_dir.mkdir(parents=True)

    hasher_bin = cache_dir / "hasher"
    hasher_src = cache_dir / "hasher.cpp"

    # Read hasher source from template
    with open(cmd_hash.HASHER_SOURCE_PATH, 'r') as f:
        hasher_source = f.read()

    # Create existing files with correct source
    hasher_src.write_text(hasher_source)
    hasher_bin.write_text("fake binary")

    with patch('os.path.expanduser', return_value=str(home_dir)):
        hasher_path = cmd_hash.get_or_compile_hasher()

        # Should return existing binary path
        assert hasher_path.endswith("hasher")
        assert hasher_bin.exists()


def test_get_or_compile_hasher_source_changed(tmp_path):
    """Test recompiling when hasher source changed."""
    cache_dir = tmp_path / ".cache" / "cptools"
    cache_dir.mkdir(parents=True)

    hasher_bin = cache_dir / "hasher"
    hasher_src = cache_dir / "hasher.cpp"

    # Create existing files with old source
    hasher_src.write_text("old source")
    hasher_bin.write_text("old binary")

    with patch('os.path.expanduser', return_value=str(tmp_path)), \
         patch('subprocess.run') as mock_run:

        mock_run.return_value.returncode = 0

        cmd_hash.get_or_compile_hasher()

        # Should have recompiled due to source change
        mock_run.assert_called_once()


def test_get_or_compile_hasher_compilation_failure(tmp_path):
    """Test error handling when hasher compilation fails."""
    with patch('os.path.expanduser', return_value=str(tmp_path)), \
         patch('subprocess.run') as mock_run:

        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "compilation error"

        with pytest.raises(SystemExit) as exc_info:
            cmd_hash.get_or_compile_hasher()
        assert exc_info.value.code == 1
