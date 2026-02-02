"""
Integration tests for commands/config.py
"""
import sys
from unittest.mock import patch
from commands import config

def test_config_opens_editor():
    """Test that config command launches the editor defined in env."""
    # Mock sys.argv to simulate running 'cptools config' with no args
    with patch.object(sys, 'argv', ['cptools-config']), \
         patch('os.environ.get', return_value='nano'), \
         patch('subprocess.run') as mock_run, \
         patch('commands.config.ensure_config') as mock_ensure, \
         patch('commands.config.get_config_path', return_value='/fake/path/config.json'):
        
        config.run()
        
        # Verify config was ensured
        mock_ensure.assert_called_once()
        # Verify editor was called with correct path
        mock_run.assert_called_with(['nano', '/fake/path/config.json'])