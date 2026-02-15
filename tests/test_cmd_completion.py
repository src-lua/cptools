"""
Integration tests for commands/completion.py
"""
import os
from unittest.mock import patch
from cptools.commands import completion

def test_completion_generate_bash(capsys):
    """Test generating bash completion script."""
    with patch('sys.argv', ['cptools-completion', '--shell', 'bash']):
        completion.run()

    captured = capsys.readouterr()
    assert "_cptools_completion()" in captured.out
    assert "complete -F _cptools_completion" in captured.out
    # Check file completion for add/rm/mark/open/test/bundle
    assert "add|rm|mark|open|test|bundle)" in captured.out
    assert 'compgen -f -X \'!*.cpp\'' in captured.out
    # Check directory completion for update/new
    assert "update|new)" in captured.out
    assert "compgen -d" in captured.out

def test_completion_generate_zsh(capsys):
    """Test generating zsh completion script."""
    with patch('sys.argv', ['cptools-completion', '--shell', 'zsh']):
        completion.run()

    captured = capsys.readouterr()
    assert "#compdef cptools cpt" in captured.out
    assert "_cptools()" in captured.out
    # Check file completion for add/rm/mark/open/test/bundle (individual cases now)
    assert "add)" in captured.out
    assert "rm)" in captured.out
    assert '_files -g "*.cpp"' in captured.out
    # Check directory completion for update/new
    assert "update)" in captured.out
    assert "_files -/" in captured.out

def test_completion_install(tmp_path):
    """Test installing completion script."""
    # Mock home directory structure
    home = str(tmp_path)
    config_dir = os.path.join(home, ".config", "cptools")
    rc_file = os.path.join(home, ".bashrc")
    
    # Create dummy rc file
    with open(rc_file, 'w') as f:
        f.write("# existing rc\n")

    # We need to mock os.path.expanduser to return our tmp_path
    # and os.environ to return bash shell
    with patch('os.path.expanduser') as mock_expand, \
         patch('os.environ.get', return_value='/bin/bash'), \
         patch('sys.argv', ['cptools-completion', '--install']):
         
        def expand_side_effect(path):
            if path.startswith("~"):
                return path.replace("~", home)
            return path
        mock_expand.side_effect = expand_side_effect
        
        completion.run()
        
        # Check script created
        script_path = os.path.join(config_dir, "completion.bash")
        assert os.path.exists(script_path)
        
        # Check rc file updated
        with open(rc_file, 'r') as f:
            content = f.read()
            assert f"source {script_path}" in content

def test_completion_install_unsupported_shell(capsys):
    """Test install fails for unsupported shell."""
    with patch('os.environ.get', return_value='/bin/fish'), \
         patch('sys.argv', ['cptools-completion', '--install']), \
         patch('sys.exit') as mock_exit:
         
        completion.run()
        
        mock_exit.assert_called_with(1)
        captured = capsys.readouterr()
        assert "Unsupported shell" in captured.out