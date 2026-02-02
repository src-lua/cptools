"""
Integration tests for commands/mark.py
"""
import os
from unittest.mock import patch
from commands import mark
from lib.fileops import read_problem_header

def test_mark_updates_status(tmp_path):
    """Test marking a problem updates its status."""
    d = str(tmp_path)
    p = os.path.join(d, "A.cpp")
    with open(p, 'w') as f:
        f.write("/**\n * Problem: A\n * Status: ~\n */")
        
    with patch('sys.argv', ['cptools-mark', 'A', 'AC', d]):
        mark.run()
        
    header = read_problem_header(p)
    assert header.status == "AC"

def test_mark_range(tmp_path):
    """Test marking a range of problems."""
    d = str(tmp_path)
    for name in ["A.cpp", "B.cpp"]:
        with open(os.path.join(d, name), 'w') as f:
            f.write(f"/**\n * Problem: {name[0]}\n * Status: ~\n */")
            
    with patch('sys.argv', ['cptools-mark', 'A~B', 'WA', d]):
        mark.run()
        
    assert read_problem_header(os.path.join(d, "A.cpp")).status == "WA"
    assert read_problem_header(os.path.join(d, "B.cpp")).status == "WA"