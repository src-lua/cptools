"""
Integration tests for commands/open.py
"""
import os
from unittest.mock import patch
# 'open' is a keyword, so we import the module carefully
from commands import open as open_cmd

def test_open_browser(tmp_path):
    """Test opening problem URL in browser."""
    d = str(tmp_path)
    p = os.path.join(d, "A.cpp")
    with open(p, 'w') as f:
        f.write("/**\n * Link: https://example.com/A\n */")
        
    with patch('sys.argv', ['cptools-open', 'A', d]), \
         patch('webbrowser.open') as mock_browser:
         
        open_cmd.run()
        
        mock_browser.assert_called_with("https://example.com/A")