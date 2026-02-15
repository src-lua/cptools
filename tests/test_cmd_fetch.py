"""
Integration tests for commands/fetch.py
"""
import os
from unittest.mock import patch, MagicMock
from cptools.commands import fetch
from cptools.lib import PlatformError

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

    with patch('cptools.commands.fetch.detect_judge', return_value=mock_judge) as mock_detect, \
         patch('sys.argv', ['cptools-fetch', 'A', d]):

        fetch.run()

        # Verify judge was called with correct URL
        mock_detect.assert_called_with("https://codeforces.com/contest/1234/problem/A")

        # Verify samples saved
        assert os.path.exists(os.path.join(d, "A_1.in"))
        with open(os.path.join(d, "A_1.in"), 'r') as f:
            assert f.read() == "1\n"

def test_fetch_authentication_error(tmp_path):
    """Test that authentication errors are displayed with helpful message."""
    d = str(tmp_path)

    # Create problem file with private group link
    with open(os.path.join(d, "A.cpp"), 'w') as f:
        f.write("/**\n * Link: https://codeforces.com/group/test/contest/123/problem/A\n */")

    # Mock judge that raises PlatformError
    mock_judge = MagicMock()
    mock_judge.fetch_samples.side_effect = PlatformError(
        "Authentication required. This appears to be a private group. "
        "Please log in to Codeforces in your browser (Firefox, Chrome, etc.) and try again."
    )

    with patch('cptools.commands.fetch.detect_judge', return_value=mock_judge), \
         patch('sys.argv', ['cptools-fetch', 'A', d]), \
         patch('cptools.commands.fetch.error') as mock_error:

        fetch.run()

        # Verify error message was displayed
        mock_error.assert_called_once()
        error_msg = mock_error.call_args[0][0]
        assert "Authentication required" in error_msg
        assert "private group" in error_msg