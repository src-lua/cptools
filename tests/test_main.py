"""
Tests for cptools.__main__

Tests the main CLI entry point including command routing,
help display, version display, and error handling.
"""
import sys
import pytest
from unittest.mock import patch, MagicMock, Mock
from cptools.__main__ import (
    get_command_description,
    print_help,
    print_version,
    main,
)


class TestGetCommandDescription:
    """Tests for get_command_description function."""

    def test_with_valid_parser_description(self):
        """Test getting description from module with valid parser."""
        mock_module = MagicMock()
        mock_parser = MagicMock()
        mock_parser.description = "Test command description"
        mock_module.get_parser.return_value = mock_parser

        result = get_command_description(mock_module)
        assert result == "Test command description"

    def test_with_parser_no_description(self):
        """Test getting description from parser without description."""
        mock_module = MagicMock()
        mock_parser = MagicMock()
        mock_parser.description = None
        mock_module.get_parser.return_value = mock_parser

        result = get_command_description(mock_module)
        assert result == "No description"

    def test_with_no_get_parser_method(self):
        """Test module without get_parser method."""
        mock_module = MagicMock(spec=[])  # Module without get_parser

        result = get_command_description(mock_module)
        assert result == "No description"

    def test_with_exception_in_get_parser(self):
        """Test exception handling when get_parser raises error."""
        mock_module = MagicMock()
        mock_module.get_parser.side_effect = Exception("Parser error")

        result = get_command_description(mock_module)
        assert result == "No description"


class TestPrintHelp:
    """Tests for print_help function."""

    def test_help_output_structure(self, capsys):
        """Test that help displays proper structure and sections."""
        with patch('cptools.__main__.COMMAND_MODULES', {}):
            print_help()

        captured = capsys.readouterr()
        assert "cptools" in captured.out
        assert "Competitive Programming Tools" in captured.out
        assert "Usage:" in captured.out
        assert "cptools <command> [args]" in captured.out
        assert "Commands:" in captured.out
        assert "cptools <command> --help" in captured.out
        assert "cptools completion --install" in captured.out

    def test_help_displays_commands(self, capsys):
        """Test that help displays available commands."""
        mock_module1 = MagicMock()
        mock_parser1 = MagicMock()
        mock_parser1.description = "First test command"
        mock_module1.get_parser.return_value = mock_parser1

        mock_module2 = MagicMock()
        mock_parser2 = MagicMock()
        mock_parser2.description = "Second test command"
        mock_module2.get_parser.return_value = mock_parser2

        mock_commands = {
            'test1': mock_module1,
            'test2': mock_module2,
        }

        with patch('cptools.__main__.COMMAND_MODULES', mock_commands):
            print_help()

        captured = capsys.readouterr()
        assert "test1" in captured.out
        assert "First test command" in captured.out
        assert "test2" in captured.out
        assert "Second test command" in captured.out

    def test_help_truncates_long_descriptions(self, capsys):
        """Test that help truncates descriptions longer than 80 characters."""
        mock_module = MagicMock()
        mock_parser = MagicMock()
        # Create a description longer than 80 chars
        long_desc = "A" * 85
        mock_parser.description = long_desc
        mock_module.get_parser.return_value = mock_parser

        mock_commands = {'longcmd': mock_module}

        with patch('cptools.__main__.COMMAND_MODULES', mock_commands):
            print_help()

        captured = capsys.readouterr()
        # Should be truncated to 77 chars + "..."
        assert "A" * 77 + "..." in captured.out
        assert long_desc not in captured.out


class TestPrintVersion:
    """Tests for print_version function."""

    def test_version_output_with_known_version(self, capsys):
        """Test version output when version is known."""
        with patch('importlib.metadata.version', return_value="1.2.3"):
            print_version()

        captured = capsys.readouterr()
        assert "cptools 1.2.3" in captured.out
        assert "Copyright" in captured.out
        assert "Lua Guimarães Fernandes" in captured.out
        assert "MIT" in captured.out
        assert "https://opensource.org/licenses/MIT" in captured.out
        assert "free software" in captured.out

    def test_version_output_with_unknown_version(self, capsys):
        """Test version output when version cannot be determined."""
        with patch('importlib.metadata.version', side_effect=Exception("Not found")):
            print_version()

        captured = capsys.readouterr()
        assert "cptools unknown" in captured.out


class TestMain:
    """Tests for main function."""

    def test_main_no_arguments_shows_help(self, capsys):
        """Test that running with no arguments shows help."""
        with patch('sys.argv', ['cptools']), \
             patch('cptools.__main__.COMMAND_MODULES', {}), \
             pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        assert "Commands:" in captured.out

    def test_main_help_flag_shows_help(self, capsys):
        """Test that -h and --help flags show help."""
        for help_flag in ['-h', '--help']:
            with patch('sys.argv', ['cptools', help_flag]), \
                 patch('cptools.__main__.COMMAND_MODULES', {}), \
                 pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Usage:" in captured.out

    def test_main_version_flag_shows_version(self, capsys):
        """Test that -v and --version flags show version."""
        for version_flag in ['-v', '--version']:
            with patch('sys.argv', ['cptools', version_flag]), \
                 patch('importlib.metadata.version', return_value="1.0.0"), \
                 pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "cptools 1.0.0" in captured.out

    def test_main_unknown_command_shows_error(self, capsys):
        """Test that unknown command shows error and help."""
        with patch('sys.argv', ['cptools', 'unknowncmd']), \
             patch('cptools.__main__.COMMAND_MODULES', {}), \
             pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        # error() writes to stderr, not stdout
        assert "Unknown command: unknowncmd" in captured.err
        assert "Usage:" in captured.out

    def test_main_valid_command_executes(self):
        """Test that valid command is executed."""
        mock_module = MagicMock()
        captured_argv = []

        def capture_argv():
            captured_argv.append(sys.argv.copy())

        mock_module.run = capture_argv

        mock_commands = {'testcmd': mock_module}

        with patch('sys.argv', ['cptools', 'testcmd', '--arg', 'value']), \
             patch('cptools.__main__.COMMAND_MODULES', mock_commands):
            main()

        # Verify run was called and sys.argv was rewritten correctly
        assert len(captured_argv) == 1
        assert captured_argv[0] == ['testcmd', '--arg', 'value']

    def test_main_command_with_no_arguments(self):
        """Test command execution without additional arguments."""
        mock_module = MagicMock()
        captured_argv = []

        def capture_argv():
            captured_argv.append(sys.argv.copy())

        mock_module.run = capture_argv

        mock_commands = {'simple': mock_module}

        with patch('sys.argv', ['cptools', 'simple']), \
             patch('cptools.__main__.COMMAND_MODULES', mock_commands):
            main()

        # Verify run was called and sys.argv was rewritten correctly
        assert len(captured_argv) == 1
        assert captured_argv[0] == ['simple']

    def test_main_command_with_multiple_arguments(self):
        """Test command execution with multiple arguments."""
        mock_module = MagicMock()
        captured_argv = []

        def capture_argv():
            captured_argv.append(sys.argv.copy())

        mock_module.run = capture_argv

        mock_commands = {'multi': mock_module}

        with patch('sys.argv', ['cptools', 'multi', 'arg1', 'arg2', '--flag']), \
             patch('cptools.__main__.COMMAND_MODULES', mock_commands):
            main()

        # Verify run was called and sys.argv was rewritten correctly
        assert len(captured_argv) == 1
        assert captured_argv[0] == ['multi', 'arg1', 'arg2', '--flag']

    def test_main_preserves_argv_for_subcommand(self):
        """Test that sys.argv is correctly rewritten for subcommand parsing."""
        mock_module = MagicMock()

        def check_argv():
            # Verify argv at the time of execution
            assert sys.argv[0] == 'fetch'
            assert '--url' in sys.argv
            assert 'https://example.com' in sys.argv

        mock_module.run = check_argv

        mock_commands = {'fetch': mock_module}

        original_argv = ['cptools', 'fetch', '--url', 'https://example.com']
        with patch('sys.argv', original_argv.copy()), \
             patch('cptools.__main__.COMMAND_MODULES', mock_commands):
            main()


class TestIntegration:
    """Integration tests for the main CLI."""

    def test_main_entry_point_exists(self):
        """Test that main entry point can be imported."""
        from cptools.__main__ import main
        assert callable(main)

    def test_command_modules_registry_loads(self):
        """Test that command modules registry is populated."""
        from cptools.__main__ import COMMAND_MODULES

        # Should have at least some standard commands
        assert isinstance(COMMAND_MODULES, dict)
        # Most installations should have basic commands
        # We don't assert specific commands to keep test resilient

    def test_help_works_with_real_commands(self, capsys):
        """Test help display with actual loaded commands."""
        # This test uses the real command registry
        print_help()

        captured = capsys.readouterr()
        assert "cptools" in captured.out
        assert "Usage:" in captured.out
        assert "Commands:" in captured.out
