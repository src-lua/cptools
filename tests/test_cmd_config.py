"""
Integration tests for commands/config.py
"""
import sys
from unittest.mock import patch, MagicMock
from cptools.commands import config

def test_config_opens_editor():
    """Test that config command launches the editor with fallback chain."""
    # Mock sys.argv to simulate running 'cptools config' with no args
    # Mock subprocess.run to simulate 'which nano' returning success (editor found)
    mock_run = MagicMock()
    mock_run.side_effect = [
        MagicMock(returncode=0),  # First call: 'which nano' succeeds
        None  # Second call: actual editor launch
    ]

    with patch.object(sys, 'argv', ['cptools-config']), \
         patch('subprocess.run', mock_run), \
         patch('cptools.commands.config.ensure_config') as mock_ensure, \
         patch('cptools.commands.config.get_config_path', return_value='/fake/path/config.json'):

        config.run()

        # Verify config was ensured
        mock_ensure.assert_called_once()
        # Verify editor was called with correct path (second call to subprocess.run)
        assert mock_run.call_count == 2
        # The second call should be the actual editor launch
        mock_run.call_args_list[1][0][0] == ['nano', '/fake/path/config.json']