"""
Integration tests for commands/config.py
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from cptools.commands import config
from cptools.commands.config import find_editor, show_vim_help


class TestFindEditor:
    """Tests for find_editor function."""

    def test_respects_editor_env_variable(self):
        """Test that $EDITOR environment variable is respected."""
        with patch.dict(os.environ, {'EDITOR': 'nano'}), \
             patch('subprocess.run', return_value=MagicMock(returncode=0)):
            editor, is_vim_like = find_editor()
            assert editor == 'nano'
            assert is_vim_like is False

    def test_detects_vim_like_editor_from_env(self):
        """Test vim-like detection from $EDITOR."""
        for vim_editor in ['vim', 'vi', 'nvim']:
            with patch.dict(os.environ, {'EDITOR': vim_editor}), \
                 patch('subprocess.run', return_value=MagicMock(returncode=0)):
                editor, is_vim_like = find_editor()
                assert editor == vim_editor
                assert is_vim_like is True

    def test_fallback_to_nano(self):
        """Test fallback to nano when $EDITOR not set."""
        with patch.dict(os.environ, {}, clear=True), \
             patch('subprocess.run') as mock_run:
            # First call (nano) succeeds
            mock_run.return_value = MagicMock(returncode=0)

            editor, is_vim_like = find_editor()
            assert editor == 'nano'
            assert is_vim_like is False

    def test_fallback_chain(self):
        """Test fallback chain when nano not available."""
        with patch.dict(os.environ, {}, clear=True), \
             patch('subprocess.run') as mock_run:
            # nano fails, vim succeeds
            mock_run.side_effect = [
                MagicMock(returncode=1),  # nano not found
                MagicMock(returncode=0),  # vim found
            ]

            editor, is_vim_like = find_editor()
            assert editor == 'vim'
            assert is_vim_like is True

    def test_ultimate_fallback_to_vi(self):
        """Test ultimate fallback to vi."""
        with patch.dict(os.environ, {}, clear=True), \
             patch('subprocess.run') as mock_run:
            # All editors fail
            mock_run.return_value = MagicMock(returncode=1)

            editor, is_vim_like = find_editor()
            assert editor == 'vi'
            assert is_vim_like is True

    def test_env_editor_not_available(self):
        """Test fallback when $EDITOR is set but not available."""
        with patch.dict(os.environ, {'EDITOR': 'nonexistent'}), \
             patch('subprocess.run') as mock_run:
            # nonexistent fails, nano succeeds
            mock_run.side_effect = [
                MagicMock(returncode=1),  # nonexistent not found
                MagicMock(returncode=0),  # nano found
            ]

            editor, is_vim_like = find_editor()
            assert editor == 'nano'
            assert is_vim_like is False

    def test_subprocess_exception_handling(self):
        """Test handling of subprocess exceptions."""
        with patch.dict(os.environ, {}, clear=True), \
             patch('subprocess.run') as mock_run:
            # First call raises exception, second succeeds
            mock_run.side_effect = [
                Exception("Command failed"),
                MagicMock(returncode=0),
            ]

            editor, is_vim_like = find_editor()
            # Should skip nano and find vim
            assert editor in ['vim', 'vi', 'nano', 'emacs']


class TestShowVimHelp:
    """Tests for show_vim_help function."""

    def test_vim_help_output(self, capsys):
        """Test vim help displays usage instructions."""
        show_vim_help()

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "Vim Quick Start:" in output
        assert "i" in output
        assert "insert mode" in output
        assert "Esc" in output
        assert ":w" in output
        assert "Save" in output or "save" in output
        assert ":q" in output
        assert "Quit" in output or "quit" in output
        assert ":wq" in output


class TestConfigRun:
    """Integration tests for config.run() function."""

    def test_config_opens_editor(self):
        """Test that config command launches the editor with fallback chain."""
        mock_run = MagicMock()
        mock_run.side_effect = [
            MagicMock(returncode=0),  # First call: 'which nano' succeeds
            None  # Second call: actual editor launch
        ]

        with patch.object(sys, 'argv', ['cptools-config']), \
             patch('subprocess.run', mock_run), \
             patch('cptools.commands.config.ensure_config') as mock_ensure, \
             patch('cptools.commands.config.get_config_path', return_value='/fake/path/config.json'):

            config.run()

            # Verify config was ensured
            mock_ensure.assert_called_once()
            # Verify editor was called with correct path (second call to subprocess.run)
            assert mock_run.call_count == 2
            # The second call should be the actual editor launch
            mock_run.call_args_list[1][0][0] == ['nano', '/fake/path/config.json']

    def test_config_with_editor_flag(self):
        """Test config with --editor flag."""
        mock_run = MagicMock()

        with patch.object(sys, 'argv', ['cptools-config', '--editor', 'vim']), \
             patch('subprocess.run', mock_run), \
             patch('cptools.commands.config.ensure_config'), \
             patch('cptools.commands.config.get_config_path', return_value='/fake/config.json'):

            config.run()

            # Verify vim was called directly
            assert mock_run.call_count == 1
            mock_run.assert_called_with(['vim', '/fake/config.json'])

    def test_config_with_short_editor_flag(self):
        """Test config with -e flag."""
        mock_run = MagicMock()

        with patch.object(sys, 'argv', ['cptools-config', '-e', 'nano']), \
             patch('subprocess.run', mock_run), \
             patch('cptools.commands.config.ensure_config'), \
             patch('cptools.commands.config.get_config_path', return_value='/fake/config.json'):

            config.run()

            # Verify nano was called
            assert mock_run.call_count == 1
            mock_run.assert_called_with(['nano', '/fake/config.json'])

    def test_config_shows_vim_help_for_vim(self, capsys):
        """Test that vim help is shown for vim-like editors."""
        with patch.object(sys, 'argv', ['cptools-config', '--editor', 'vim']), \
             patch('subprocess.run'), \
             patch('cptools.commands.config.ensure_config'), \
             patch('cptools.commands.config.get_config_path', return_value='/fake/config.json'):

            config.run()

            captured = capsys.readouterr()
            output = captured.out + captured.err
            assert "Vim Quick Start:" in output

    def test_config_no_vim_help_for_nano(self, capsys):
        """Test that vim help is NOT shown for nano."""
        with patch.object(sys, 'argv', ['cptools-config', '--editor', 'nano']), \
             patch('subprocess.run'), \
             patch('cptools.commands.config.ensure_config'), \
             patch('cptools.commands.config.get_config_path', return_value='/fake/config.json'):

            config.run()

            captured = capsys.readouterr()
            output = captured.out + captured.err
            assert "Vim Quick Start:" not in output

    def test_config_editor_not_found(self, capsys):
        """Test error handling when editor is not found."""
        with patch.object(sys, 'argv', ['cptools-config', '--editor', 'nonexistent']), \
             patch('subprocess.run', side_effect=FileNotFoundError()), \
             patch('cptools.commands.config.ensure_config'), \
             patch('cptools.commands.config.get_config_path', return_value='/fake/config.json'), \
             pytest.raises(SystemExit) as exc_info:

            config.run()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err
        assert "Please install a text editor" in captured.err

    def test_config_creates_config_if_missing(self):
        """Test that config file is created if it doesn't exist."""
        mock_ensure = MagicMock()

        with patch.object(sys, 'argv', ['cptools-config']), \
             patch('subprocess.run') as mock_run, \
             patch('cptools.commands.config.ensure_config', mock_ensure), \
             patch('cptools.commands.config.get_config_path', return_value='/fake/config.json'), \
             patch('cptools.commands.config.find_editor', return_value=('nano', False)):

            config.run()

            # Verify ensure_config was called
            mock_ensure.assert_called_once()

    def test_config_displays_info(self, capsys):
        """Test that config displays path and editor info."""
        with patch.object(sys, 'argv', ['cptools-config', '--editor', 'nano']), \
             patch('subprocess.run'), \
             patch('cptools.commands.config.ensure_config'), \
             patch('cptools.commands.config.get_config_path', return_value='/fake/config.json'):

            config.run()

            captured = capsys.readouterr()
            output = captured.out + captured.err
            assert "Opening config:" in output
            assert "/fake/config.json" in output
            assert "Editor:" in output
            assert "nano" in output