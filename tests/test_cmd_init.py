"""
Integration tests for commands/init.py
"""
import os
from unittest.mock import patch
from commands import init

def test_init_creates_structure(tmp_path):
    """Test initialization of repo structure."""
    target_dir = str(tmp_path)
    
    with patch('commands.init.ensure_config') as mock_ensure, \
         patch('subprocess.run') as mock_run:
        
        mock_run.return_value.returncode = 0
        
        # Call main with directory arg
        with patch('sys.argv', ['cptools-init', target_dir]):
            init.run()
            
        # Check directories
        assert os.path.exists(os.path.join(target_dir, "Codeforces"))
        assert os.path.exists(os.path.join(target_dir, "AtCoder"))
        
        # Check .gitignore
        assert os.path.exists(os.path.join(target_dir, ".gitignore"))
        
        # Check git init called
        mock_run.assert_called()
        args = mock_run.call_args[0][0]
        assert args[0] == 'git'
        assert args[1] == 'init'

def test_init_nogit(tmp_path):
    """Test initialization with --nogit."""
    target_dir = str(tmp_path)

    with patch('commands.init.ensure_config'), \
         patch('subprocess.run') as mock_run:

        with patch('sys.argv', ['cptools-init', target_dir, '--nogit']):
            init.run()

        # Git init should not be called
        mock_run.assert_not_called()

        # .gitignore should NOT be created when --nogit is used (Q11 fix)
        assert not os.path.exists(os.path.join(target_dir, ".gitignore"))

def test_init_without_nogit_creates_gitignore(tmp_path):
    """Test that .gitignore is created when --nogit is NOT used (Q11)."""
    target_dir = str(tmp_path)

    with patch('commands.init.ensure_config'), \
         patch('subprocess.run') as mock_run:

        mock_run.return_value.returncode = 0

        with patch('sys.argv', ['cptools-init', target_dir]):
            init.run()

        # .gitignore SHOULD be created when --nogit is NOT used
        gitignore_path = os.path.join(target_dir, ".gitignore")
        assert os.path.exists(gitignore_path)

        # Verify content
        with open(gitignore_path, 'r') as f:
            content = f.read()
            assert '*.out' in content
            assert '*.hashed' in content
            assert '_stress_*' in content