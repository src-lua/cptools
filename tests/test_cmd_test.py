"""
Integration tests for commands/test.py
"""
import os
import sys
import subprocess
from unittest.mock import patch, MagicMock
from commands import test
import pytest

def test_run_samples_success(tmp_path):
    """Test running solution against samples successfully."""
    temp_dir = str(tmp_path)
    problem = "A"

    # Create dummy source file
    with open(os.path.join(temp_dir, "A.cpp"), 'w') as f:
        f.write("int main() {}")

    # Mock compilation to succeed
    mock_compile_res = MagicMock(success=True, binary_path=os.path.join(temp_dir, ".A"))

    # Mock samples
    samples = [{'in': 'in1', 'out': 'out1', 'num': 1}]

    # Mock subprocess.run for the execution of the binary
    # We need to mock it to return the "expected" output so the test passes
    mock_exec_res = MagicMock(stdout="out1\n", returncode=0)

    with patch.object(sys, 'argv', ['cptools-test', 'A', temp_dir]), \
         patch('commands.test.load_config', return_value={}), \
         patch('commands.test.compile_from_config', return_value=mock_compile_res) as mock_compile, \
         patch('commands.test.find_samples', return_value=samples), \
         patch('subprocess.run', return_value=mock_exec_res) as mock_run, \
         patch('sys.exit') as mock_exit, \
         patch('builtins.open', create=True) as mock_open: # Mock open for reading sample files

        # We need to allow open() to work for real files (like A.cpp check) but mock for sample reading
        # This is tricky with global open patch.
        # Alternative: Let find_samples return real file paths that we create.
        pass

    # Let's retry with real files for samples to simplify mocking
    sample_in = os.path.join(temp_dir, "A_1.in")
    sample_out = os.path.join(temp_dir, "A_1.out")
    with open(sample_in, 'w') as f: f.write("input")
    with open(sample_out, 'w') as f: f.write("expected")

    # Mock Popen instead of run
    mock_process = MagicMock()
    mock_process.pid = 12345
    mock_process.communicate.return_value = ("expected\n", "")

    with patch.object(sys, 'argv', ['cptools-test', 'A', temp_dir]), \
         patch('commands.test.load_config', return_value={}), \
         patch('commands.test.compile_from_config', return_value=mock_compile_res), \
         patch('subprocess.Popen', return_value=mock_process), \
         patch('sys.stdin.isatty', return_value=True): # Simulate terminal

        # Expect sys.exit(0) on success
        try:
            test.run()
        except SystemExit as e:
            assert e.code == 0


def test_run_samples_failure(tmp_path):
    """Test running solution with wrong output."""
    temp_dir = str(tmp_path)

    # Create source and samples
    with open(os.path.join(temp_dir, "B.cpp"), 'w') as f:
        f.write("int main() {}")

    sample_in = os.path.join(temp_dir, "B_1.in")
    sample_out = os.path.join(temp_dir, "B_1.out")
    with open(sample_in, 'w') as f:
        f.write("1 2")
    with open(sample_out, 'w') as f:
        f.write("3")

    mock_compile_res = MagicMock(success=True, binary_path=os.path.join(temp_dir, ".B"))

    # Mock Popen
    mock_process = MagicMock()
    mock_process.pid = 12345
    mock_process.communicate.return_value = ("999\n", "")

    with patch.object(sys, 'argv', ['cptools-test', 'B', temp_dir]), \
         patch('commands.test.load_config', return_value={}), \
         patch('commands.test.compile_from_config', return_value=mock_compile_res), \
         patch('subprocess.Popen', return_value=mock_process), \
         patch('sys.stdin.isatty', return_value=True):

        # Expect sys.exit(1) on failure
        with pytest.raises(SystemExit) as exc_info:
            test.run()
        assert exc_info.value.code == 1


def test_compilation_failure(tmp_path):
    """Test behavior when compilation fails."""
    temp_dir = str(tmp_path)

    with open(os.path.join(temp_dir, "C.cpp"), 'w') as f:
        f.write("int main() {}")

    mock_compile_res = MagicMock(success=False, stderr="error: syntax error")

    with patch.object(sys, 'argv', ['cptools-test', 'C', temp_dir]), \
         patch('commands.test.load_config', return_value={}), \
         patch('commands.test.compile_from_config', return_value=mock_compile_res):

        with pytest.raises(SystemExit) as exc_info:
            test.run()
        assert exc_info.value.code == 1


def test_file_not_found(tmp_path):
    """Test error when source file doesn't exist."""
    temp_dir = str(tmp_path)

    with patch.object(sys, 'argv', ['cptools-test', 'NonExistent', temp_dir]), \
         patch('commands.test.load_config', return_value={}):

        with pytest.raises(SystemExit) as exc_info:
            test.run()
        assert exc_info.value.code == 1


def test_timeout_handling(tmp_path):
    """Test timeout handling during execution."""
    temp_dir = str(tmp_path)

    with open(os.path.join(temp_dir, "D.cpp"), 'w') as f:
        f.write("int main() {}")

    sample_in = os.path.join(temp_dir, "D_1.in")
    sample_out = os.path.join(temp_dir, "D_1.out")
    with open(sample_in, 'w') as f:
        f.write("input")
    with open(sample_out, 'w') as f:
        f.write("output")

    mock_compile_res = MagicMock(success=True, binary_path=os.path.join(temp_dir, ".D"))

    # Mock Popen that times out
    mock_process = MagicMock()
    mock_process.pid = 12345
    mock_process.communicate.side_effect = subprocess.TimeoutExpired('cmd', 10)
    mock_process.kill = MagicMock()
    mock_process.wait = MagicMock()

    with patch.object(sys, 'argv', ['cptools-test', 'D', temp_dir]), \
         patch('commands.test.load_config', return_value={}), \
         patch('commands.test.compile_from_config', return_value=mock_compile_res), \
         patch('subprocess.Popen', return_value=mock_process), \
         patch('sys.stdin.isatty', return_value=True):

        with pytest.raises(SystemExit) as exc_info:
            test.run()
        assert exc_info.value.code == 1


# Note: test_add_mode tests are skipped because they require TTY interaction
# which is difficult to mock properly in unit tests. The --add functionality
# is better tested manually or with integration tests.


def test_sample_without_expected_output(tmp_path):
    """Test running sample that has no expected output file."""
    temp_dir = str(tmp_path)

    with open(os.path.join(temp_dir, "G.cpp"), 'w') as f:
        f.write("int main() {}")

    # Create input without output
    sample_in = os.path.join(temp_dir, "G_1.in")
    with open(sample_in, 'w') as f:
        f.write("test input")

    mock_compile_res = MagicMock(success=True, binary_path=os.path.join(temp_dir, ".G"))

    # Mock Popen
    mock_process = MagicMock()
    mock_process.pid = 12345
    mock_process.communicate.return_value = ("result\n", "")

    with patch.object(sys, 'argv', ['cptools-test', 'G', temp_dir]), \
         patch('commands.test.load_config', return_value={}), \
         patch('commands.test.compile_from_config', return_value=mock_compile_res), \
         patch('subprocess.Popen', return_value=mock_process), \
         patch('sys.stdin.isatty', return_value=True):

        with pytest.raises(SystemExit) as exc_info:
            test.run()
        # Should still pass since it's just showing output
        assert exc_info.value.code == 0
