"""
Integration tests for commands/commit.py
"""
import os
from unittest.mock import patch, MagicMock
from commands import commit

def test_commit_directory_success(tmp_path):
    """Test successful commit of a directory."""
    root = str(tmp_path)
    contest_dir = os.path.join(root, "Codeforces", "123")
    os.makedirs(contest_dir)
    
    with patch('commands.commit.get_repo_root', return_value=root), \
         patch('subprocess.run') as mock_run, \
         patch('sys.argv', ['cptools-commit', contest_dir]):
         
        # Mock git calls behavior
        def side_effect(cmd, **kwargs):
            m = MagicMock()
            # git diff --cached --quiet returns 1 if there are changes, 0 if clean
            if 'diff' in cmd:
                m.returncode = 1 
            else:
                m.returncode = 0
            return m
        
        mock_run.side_effect = side_effect
        
        commit.run()
        
        # Verify sequence: git add, git diff, git commit, git push
        assert mock_run.call_count >= 4
        
        # Check commit message contains relative path
        commit_args = [c[0][0] for c in mock_run.call_args_list if 'commit' in c[0][0]]
        assert len(commit_args) == 1
        assert "Codeforces/123" in commit_args[0]

def test_commit_no_changes(tmp_path):
    """Test commit aborts if no changes staged."""
    root = str(tmp_path)
    contest_dir = os.path.join(root, "Codeforces", "123")
    os.makedirs(contest_dir)
    
    with patch('commands.commit.get_repo_root', return_value=root), \
         patch('subprocess.run') as mock_run, \
         patch('sys.argv', ['cptools-commit', contest_dir]):
         
        # Mock git diff returning 0 (no changes)
        def side_effect(cmd, **kwargs):
            m = MagicMock()
            if 'diff' in cmd:
                m.returncode = 0 
            else:
                m.returncode = 0
            return m
        mock_run.side_effect = side_effect
        
        # Should exit gracefully
        try:
            commit.run()
        except SystemExit as e:
            assert e.code == 0
            
        # Should NOT have called git commit or push
        commit_calls = [c for c in mock_run.call_args_list if 'commit' in c[0][0]]
        push_calls = [c for c in mock_run.call_args_list if 'push' in c[0][0]]
        assert len(commit_calls) == 0
        assert len(push_calls) == 0

def test_commit_all(tmp_path):
    """Test committing all changed directories."""
    root = str(tmp_path)
    # Setup two contests
    c1 = os.path.join(root, "Codeforces", "1")
    c2 = os.path.join(root, "Codeforces", "2")
    os.makedirs(c1)
    os.makedirs(c2)
    
    # Add .cpp files so they are detected as contests
    with open(os.path.join(c1, "A.cpp"), 'w') as f: f.write("")
    with open(os.path.join(c2, "B.cpp"), 'w') as f: f.write("")

    with patch('commands.commit.get_repo_root', return_value=root), \
         patch('commands.commit.PLATFORM_DIRS', ['Codeforces']), \
         patch('subprocess.run') as mock_run, \
         patch('sys.argv', ['cptools-commit', '--all']):
         
        # Assume all have changes
        mock_run.return_value.returncode = 1 # for diff (changes exist)
        # For add/commit/push returncode 0 is usually expected for success, 
        # but our code checks != 0 for failure. 
        # We need to be careful with the mock return value for different calls if logic is strict.
        # But commit_directory checks diff returncode == 0 for "no changes".
        # So if we return 1 globally, diff says "changes exist", but add/commit might fail if they check == 0.
        
        # Better mock:
        def side_effect(cmd, **kwargs):
            m = MagicMock()
            if 'diff' in cmd:
                m.returncode = 1 # Changes exist
            else:
                m.returncode = 0 # Success
            return m
        mock_run.side_effect = side_effect
        
        commit.run()
        
        # Should have tried to commit both contests
        commit_calls = [c for c in mock_run.call_args_list if 'commit' in c[0][0]]
        assert len(commit_calls) == 2
        
        # Should push once at the end
        push_calls = [c for c in mock_run.call_args_list if 'push' in c[0][0]]
        assert len(push_calls) == 1