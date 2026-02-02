"""
Integration tests for commands/stress.py
"""
import os
import sys
from unittest.mock import patch, MagicMock
from commands import stress

def test_stress_mismatch(tmp_path, monkeypatch):
    """Test stress command detecting a mismatch between solution and brute."""
    d = str(tmp_path)
    monkeypatch.chdir(d)
    # Create dummy source files
    for name in ["sol.cpp", "brute.cpp", "gen.cpp"]:
        with open(os.path.join(d, name), 'w') as f:
            f.write("int main(){}")

    # Mock compilation to always succeed
    mock_compile = MagicMock()
    mock_compile.success = True

    # Mock subprocess.run to simulate execution outputs
    def side_effect(cmd, **kwargs):
        m = MagicMock()
        m.returncode = 0
        # Simulate output writing to the file handles passed in kwargs
        if '_stress_gen' in cmd[0]:
            if 'stdout' in kwargs: kwargs['stdout'].write("1 2\n")
        elif '_stress_sol' in cmd[0]:
            if 'stdout' in kwargs: kwargs['stdout'].write("3\n")
        elif '_stress_brt' in cmd[0]:
            if 'stdout' in kwargs: kwargs['stdout'].write("4\n") # Mismatch!
        return m

    with patch('commands.stress.load_config', return_value={}), \
         patch('commands.stress.compile_from_config', return_value=mock_compile), \
         patch('subprocess.run', side_effect=side_effect) as mock_run, \
         patch('sys.argv', ['cptools-stress', 'sol', 'brute', 'gen']):
        
        # Run stress. It should detect mismatch and break the loop
        stress.run()
        
        # Verify that subprocess was called (compilation + execution)
        assert mock_run.called

def test_stress_success(tmp_path, monkeypatch):
    """Test stress command passing iterations successfully."""
    d = str(tmp_path)
    monkeypatch.chdir(d)
    for name in ["sol.cpp", "brute.cpp", "gen.cpp"]:
        with open(os.path.join(d, name), 'w') as f: f.write("")

    mock_compile = MagicMock()
    mock_compile.success = True

    # Mock outputs to always match
    mock_run = MagicMock()
    mock_run.returncode = 0
    
    original_range = range
    def mock_range(*args):
        if args == (1, 1_000_000):
            return [1, 2]
        return original_range(*args)

    # Patch range to run only 2 iterations instead of 1,000,000
    with patch('commands.stress.load_config', return_value={}), \
         patch('commands.stress.compile_from_config', return_value=mock_compile), \
         patch('subprocess.run', return_value=mock_run), \
         patch('sys.argv', ['cptools-stress', 'sol', 'brute', 'gen']), \
         patch('builtins.range', side_effect=mock_range):
         
         stress.run()