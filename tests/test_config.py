"""
Tests for lib/config.py - Configuration management.
"""
import json
from unittest.mock import patch, mock_open
from lib import config

def test_get_config_path():
    """Test that get_config_path returns the constant path."""
    assert config.get_config_path() == config.CONFIG_PATH

def test_ensure_config_creates_if_missing():
    """Test that config file is created with defaults if missing."""
    with patch('os.path.exists', return_value=False), \
         patch('os.makedirs') as mock_makedirs, \
         patch('builtins.open', mock_open()) as mock_file:
        
        config.ensure_config()
        
        mock_makedirs.assert_called_with(config.CONFIG_DIR, exist_ok=True)
        mock_file.assert_called_with(config.CONFIG_PATH, 'w')
        
        # Verify that something was written (json dump)
        handle = mock_file()
        assert handle.write.called

def test_ensure_config_does_nothing_if_exists():
    """Test that nothing happens if config file already exists."""
    with patch('os.path.exists', return_value=True), \
         patch('os.makedirs') as mock_makedirs, \
         patch('builtins.open', mock_open()) as mock_file:
        
        config.ensure_config()
        
        mock_makedirs.assert_not_called()
        mock_file.assert_not_called()

def test_load_config_merges_user_config():
    """Test that user config overrides defaults."""
    user_data = {"author": "TestUser", "compiler": "clang++"}
    mock_json = json.dumps(user_data)
    
    with patch('lib.config.ensure_config'), \
         patch('builtins.open', mock_open(read_data=mock_json)):
        
        cfg = config.load_config()
        
        assert cfg["author"] == "TestUser"
        assert cfg["compiler"] == "clang++"
        # Default value preserved for missing key
        assert cfg["default_group_id"] == config.DEFAULTS["default_group_id"]

def test_load_config_handles_errors():
    """Test that defaults are returned on file error or invalid JSON."""
    # Case 1: IOError
    with patch('lib.config.ensure_config'), \
         patch('builtins.open', side_effect=IOError):
        assert config.load_config() == config.DEFAULTS

    # Case 2: JSONDecodeError
    with patch('lib.config.ensure_config'), \
         patch('builtins.open', mock_open(read_data="{invalid_json")):
        assert config.load_config() == config.DEFAULTS