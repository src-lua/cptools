"""
Integration tests for commands/status.py
"""
import os
from unittest.mock import patch
from commands import status

def test_status_display(tmp_path, capsys):
    """Test status command output."""
    d = str(tmp_path)
    
    # Create dummy problems
    with open(os.path.join(d, "A.cpp"), 'w') as f:
        f.write("/**\n * Problem: A\n * Status: AC\n */")
    with open(os.path.join(d, "B.cpp"), 'w') as f:
        f.write("/**\n * Problem: B\n * Status: WA\n */")
        
    with patch('sys.argv', ['cptools-status', d]):
        status.run()
        
    captured = capsys.readouterr()
    output = captured.out + captured.err
    
    assert "A" in output
    assert "B" in output
    # Check for status indicators (either text or emoji depending on implementation)
    assert "AC" in output or "✅" in output
    assert "WA" in output or "⚠️" in output