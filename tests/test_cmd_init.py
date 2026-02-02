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
            
        mock_run.assert_not_called()