"""
Integration tests for commands/fetch.py
"""
import os
from unittest.mock import patch, MagicMock
from commands import fetch

def test_fetch_samples_from_file_link(tmp_path):
    """Test fetching samples using link from local file header."""
    d = str(tmp_path)
    
    # Create problem file with link
    with open(os.path.join(d, "A.cpp"), 'w') as f:
        f.write("/**\n * Link: https://codeforces.com/contest/1234/problem/A\n */")

    # Mock judge
    mock_judge = MagicMock()
    mock_judge.fetch_samples.return_value = [
        MagicMock(input="1", output="2\n")
    ]

    with patch('commands.fetch.detect_judge', return_value=mock_judge) as mock_detect, \
         patch('sys.argv', ['cptools-fetch', 'A', d]):
        
        fetch.run()
        
        # Verify judge was called with correct URL
        mock_detect.assert_called_with("https://codeforces.com/contest/1234/problem/A")
        
        # Verify samples saved
        assert os.path.exists(os.path.join(d, "A_1.in"))
        with open(os.path.join(d, "A_1.in"), 'r') as f:
            assert f.read() == "1\n"