"""
Tests to verify flag consistency across commands (Q13).
"""
import os
from unittest.mock import patch
from commands import clean, commit, update, bundle, init


def test_clean_short_flag_all_works(tmp_path, monkeypatch):
    """Test that clean -a works same as --all."""
    monkeypatch.chdir(tmp_path)

    with patch('commands.clean.PLATFORM_DIRS', ['TestPlatform']), \
         patch('commands.clean.ROOT_DIR', str(tmp_path)):

        # Create test structure
        test_dir = tmp_path / 'TestPlatform'
        test_dir.mkdir()
        (test_dir / 'test.out').touch()

        # Test -a flag
        with patch('sys.argv', ['cptools-clean', '-a']):
            clean.run()

        # Should have been removed
        assert not (test_dir / 'test.out').exists()


def test_clean_short_flag_recursive_works(tmp_path, monkeypatch):
    """Test that clean -r works same as --recursive."""
    monkeypatch.chdir(tmp_path)

    # Create nested structure
    subdir = tmp_path / 'subdir'
    subdir.mkdir()
    (subdir / 'test.out').touch()

    with patch('sys.argv', ['cptools-clean', str(tmp_path), '-r']):
        clean.run()

    # Should have been removed recursively
    assert not (subdir / 'test.out').exists()


def test_commit_short_flag_all_works(tmp_path, monkeypatch):
    """Test that commit -a works same as --all."""
    monkeypatch.chdir(tmp_path)

    with patch('commands.commit.get_repo_root', return_value=str(tmp_path)), \
         patch('commands.commit.commit_all') as mock_commit_all:

        with patch('sys.argv', ['cptools-commit', '-a']):
            commit.run()

        # Should have called commit_all
        mock_commit_all.assert_called_once()


def test_update_short_flag_all_works(tmp_path, monkeypatch):
    """Test that update -a works same as --all."""
    monkeypatch.chdir(tmp_path)

    with patch('commands.update.update_all') as mock_update_all:
        with patch('sys.argv', ['cptools-update', '-a']):
            update.run()

        # Should have called update_all
        mock_update_all.assert_called_once()


def test_bundle_long_flag_output_works(tmp_path, monkeypatch):
    """Test that bundle --output works same as -o."""
    monkeypatch.chdir(tmp_path)

    # Create test file
    (tmp_path / 'A.cpp').write_text('#include <iostream>\nint main() {}')

    with patch('commands.bundle.load_config', return_value={}):
        with patch('sys.argv', ['cptools-bundle', 'A', '--output', 'out.cpp']):
            bundle.run()

    # Output file should exist
    assert (tmp_path / 'out.cpp').exists()


def test_bundle_long_flag_in_place_works(tmp_path, monkeypatch):
    """Test that bundle --in-place works same as -i."""
    monkeypatch.chdir(tmp_path)

    # Create test file
    content = '#include <iostream>\nint main() {}'
    (tmp_path / 'A.cpp').write_text(content)

    with patch('commands.bundle.load_config', return_value={}):
        with patch('sys.argv', ['cptools-bundle', 'A', '--in-place']):
            bundle.run()

    # File should still exist (bundled in place)
    assert (tmp_path / 'A.cpp').exists()


def test_init_no_git_flag_works(tmp_path):
    """Test that init --no-git works correctly."""
    target_dir = str(tmp_path)

    with patch('commands.init.ensure_config'), \
         patch('subprocess.run') as mock_run:

        with patch('sys.argv', ['cptools-init', target_dir, '--no-git']):
            init.run()

        # Git init should not be called
        mock_run.assert_not_called()

        # .gitignore should NOT be created
        assert not os.path.exists(os.path.join(target_dir, ".gitignore"))
