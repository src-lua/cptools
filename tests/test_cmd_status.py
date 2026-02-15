"""
Integration tests for commands/status.py
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from cptools.commands import status
from cptools.commands.status import (
    get_emoji_display_width,
    get_display_mode,
    calculate_grid_columns,
    display_problems,
    add_header_to_file,
)


class TestGetEmojiDisplayWidth:
    """Tests for get_emoji_display_width function."""

    def test_manual_emoji_widths(self):
        """Test manually configured emoji widths."""
        assert get_emoji_display_width('⬜') == 2
        assert get_emoji_display_width('⏱️') == 1
        assert get_emoji_display_width('⚠️') == 1

    def test_emoji_with_wcwidth(self):
        """Test emoji width using wcwidth if available."""
        try:
            import wcwidth
            # If wcwidth is available, it should be used
            width = get_emoji_display_width('✅')
            assert width in [1, 2]  # Valid display widths
        except ImportError:
            pytest.skip("wcwidth not available")

    def test_emoji_codepoint_ranges(self):
        """Test emoji width based on Unicode codepoint ranges."""
        # U+1F000 - U+1FFFF range (should return 2)
        assert get_emoji_display_width('😀') == 2  # U+1F600

        # Specific codepoints (should return 2)
        assert get_emoji_display_width('✅') in [1, 2]  # U+2705
        assert get_emoji_display_width('❌') == 2  # U+274C

    def test_empty_emoji(self):
        """Test empty emoji string."""
        assert get_emoji_display_width('') == 2

    def test_fallback_width(self):
        """Test fallback width for unknown emojis."""
        # Regular ASCII character
        width = get_emoji_display_width('A')
        assert width in [1, 2]  # Should fallback to default


class TestGetDisplayMode:
    """Tests for get_display_mode function."""

    def test_force_compact_flag(self):
        """Test --grid flag forces grid mode."""
        args = MagicMock(force_compact=True, wide=False)
        mode = get_display_mode(args, terminal_width=100)
        assert mode == 'grid'

    def test_wide_flag(self):
        """Test --wide flag forces normal mode."""
        args = MagicMock(force_compact=False, wide=True)
        mode = get_display_mode(args, terminal_width=30)
        assert mode == 'normal'

    def test_auto_mode_narrow_terminal(self):
        """Test auto mode with narrow terminal uses grid."""
        args = MagicMock(force_compact=False, wide=False)
        mode = get_display_mode(args, terminal_width=40)
        assert mode == 'grid'

    def test_auto_mode_wide_terminal(self):
        """Test auto mode with wide terminal uses normal."""
        args = MagicMock(force_compact=False, wide=False)
        mode = get_display_mode(args, terminal_width=80)
        assert mode == 'normal'


class TestCalculateGridColumns:
    """Tests for calculate_grid_columns function."""

    def test_minimum_columns(self):
        """Test minimum of 1 column."""
        columns = calculate_grid_columns(5)
        assert columns == 1

    def test_maximum_columns(self):
        """Test maximum of 4 columns."""
        columns = calculate_grid_columns(200)
        assert columns == 4

    def test_various_widths(self):
        """Test column calculation for various terminal widths."""
        assert calculate_grid_columns(20) >= 1
        assert calculate_grid_columns(40) >= 1
        assert calculate_grid_columns(80) <= 4
        assert calculate_grid_columns(120) <= 4


class TestDisplayProblems:
    """Tests for display_problems function."""

    def test_grid_mode_display(self, capsys):
        """Test grid mode problem display."""
        problems = [
            ('A', '✅', 'AC', 'Problem A'),
            ('B', '⚠️', 'WA', 'Problem B'),
            ('C', '⬜', '~', 'Problem C'),
        ]
        display_problems(problems, 'grid', 80)

        captured = capsys.readouterr()
        # log() writes to stderr
        assert 'A' in captured.err
        assert 'B' in captured.err
        assert 'C' in captured.err

    def test_normal_mode_display(self, capsys):
        """Test normal mode problem display."""
        problems = [
            ('A', '✅', 'AC', 'Problem A'),
            ('B', '⚠️', 'WA', 'Problem B'),
        ]
        display_problems(problems, 'normal', 80)

        captured = capsys.readouterr()
        # log() writes to stderr
        assert 'A' in captured.err
        assert 'Problem A' in captured.err
        assert 'B' in captured.err
        assert 'Problem B' in captured.err

    def test_normal_mode_with_empty_status(self, capsys):
        """Test normal mode with empty/pending status."""
        problems = [('A', '⬜', '~', 'Problem A')]
        display_problems(problems, 'normal', 80)

        captured = capsys.readouterr()
        # log() writes to stderr
        assert 'A' in captured.err


class TestAddHeaderToFile:
    """Tests for add_header_to_file function."""

    def test_add_header_to_plain_file(self, tmp_path):
        """Test adding header to file without one."""
        filepath = tmp_path / "test.cpp"
        original_content = "int main() { return 0; }\n"
        filepath.write_text(original_content)

        with patch('cptools.commands.status.load_config', return_value={'author': 'Test Author'}):
            add_header_to_file(str(filepath), 'A')

        content = filepath.read_text()
        assert '/**' in content
        assert 'Author:' in content
        assert 'Test Author' in content
        assert 'Problem:' in content
        assert 'A' in content
        assert 'int main()' in content  # Original content preserved


class TestStatusRun:
    """Integration tests for status.run() function."""

    def test_status_display(self, tmp_path, capsys):
        """Test status command output."""
        d = str(tmp_path)

        # Create dummy problems
        with open(os.path.join(d, "A.cpp"), 'w') as f:
            f.write("/**\n * Problem: A\n * Status: AC\n */\nint main() {}")
        with open(os.path.join(d, "B.cpp"), 'w') as f:
            f.write("/**\n * Problem: B\n * Status: WA\n */\nint main() {}")

        with patch('sys.argv', ['cptools-status', d]):
            status.run()

        captured = capsys.readouterr()
        output = captured.out + captured.err

        assert "A" in output
        assert "B" in output

    def test_status_invalid_directory(self, capsys):
        """Test status with invalid directory."""
        with patch('sys.argv', ['cptools-status', '/nonexistent/path']), \
             pytest.raises(SystemExit) as exc_info:
            status.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "not a valid directory" in captured.err

    def test_status_no_cpp_files(self, tmp_path, capsys):
        """Test status with directory containing no .cpp files."""
        d = str(tmp_path)

        with patch('sys.argv', ['cptools-status', d]), \
             pytest.raises(SystemExit) as exc_info:
            status.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "No .cpp files found" in captured.err

    def test_status_with_files_without_headers(self, tmp_path, capsys):
        """Test status with files that don't have headers."""
        d = str(tmp_path)

        # Create file without header
        with open(os.path.join(d, "A.cpp"), 'w') as f:
            f.write("int main() { return 0; }\n")

        # Simulate user declining to add headers
        with patch('sys.argv', ['cptools-status', d]), \
             patch('builtins.input', return_value='n'), \
             patch('cptools.commands.status.load_config', return_value={'author': 'Test'}):
            status.run()

        captured = capsys.readouterr()
        assert "without cptools headers" in captured.err

    def test_status_add_headers_to_files(self, tmp_path, capsys):
        """Test adding headers to files without them."""
        d = str(tmp_path)

        # Create file without header
        filepath = os.path.join(d, "A.cpp")
        with open(filepath, 'w') as f:
            f.write("int main() { return 0; }\n")

        # Simulate user accepting to add headers
        with patch('sys.argv', ['cptools-status', d]), \
             patch('builtins.input', return_value='y'), \
             patch('cptools.commands.status.load_config', return_value={'author': 'Test'}):
            status.run()

        # Check header was added
        with open(filepath, 'r') as f:
            content = f.read()
        assert '/**' in content
        assert 'Author:' in content

    def test_status_grid_mode(self, tmp_path, capsys):
        """Test status with --grid flag."""
        d = str(tmp_path)

        with open(os.path.join(d, "A.cpp"), 'w') as f:
            f.write("/**\n * Problem: A\n * Status: AC\n */")

        with patch('sys.argv', ['cptools-status', d, '--grid']):
            status.run()

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "A" in output

    def test_status_wide_mode(self, tmp_path, capsys):
        """Test status with --wide flag."""
        d = str(tmp_path)

        with open(os.path.join(d, "A.cpp"), 'w') as f:
            f.write("/**\n * Problem: A\n * Status: AC\n */")

        with patch('sys.argv', ['cptools-status', d, '--wide']):
            status.run()

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "A" in output

    def test_status_counts_different_statuses(self, tmp_path, capsys):
        """Test status counts AC, WA, TLE, etc."""
        d = str(tmp_path)

        statuses = [
            ('A.cpp', 'AC'),
            ('B.cpp', 'WA'),
            ('C.cpp', 'TLE'),
            ('D.cpp', '~'),
        ]

        for filename, status_val in statuses:
            with open(os.path.join(d, filename), 'w') as f:
                f.write(f"/**\n * Problem: {filename[0]}\n * Status: {status_val}\n */")

        with patch('sys.argv', ['cptools-status', d]):
            status.run()

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "1/4 solved" in output or "AC" in output
        assert "pending" in output

    def test_status_default_directory(self, tmp_path, capsys, monkeypatch):
        """Test status uses current directory by default."""
        monkeypatch.chdir(tmp_path)

        with open(tmp_path / "A.cpp", 'w') as f:
            f.write("/**\n * Problem: A\n * Status: AC\n */")

        with patch('sys.argv', ['cptools-status']):
            status.run()

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "A" in output