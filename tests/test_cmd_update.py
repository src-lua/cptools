"""
Integration tests for commands/update.py
"""
import os
from unittest.mock import patch
from commands import update

def test_update_single_directory(tmp_path):
    """Test updating info.md in a single directory."""
    d = str(tmp_path)
    
    # Create dummy problem files
    # A.cpp is AC
    with open(os.path.join(d, "A.cpp"), 'w') as f:
        f.write("/**\n * Problem: A\n * Status: AC\n * Link: http://cf/A\n */")
    
    # B.cpp is WA
    with open(os.path.join(d, "B.cpp"), 'w') as f:
        f.write("/**\n * Problem: B\n * Status: WA\n */")

    # C.cpp is Pending (~)
    with open(os.path.join(d, "C.cpp"), 'w') as f:
        f.write("/**\n * Problem: C\n * Status: ~\n */")

    with patch('sys.argv', ['cptools-update', d]):
        update.run()

    info_md = os.path.join(d, "info.md")
    assert os.path.exists(info_md)
    
    with open(info_md, 'r') as f:
        content = f.read()
        # Check for emojis/status
        assert "✅" in content  # AC
        assert "⚠️" in content  # WA
        assert "⬜" in content  # Pending
        
        # Check progress summary
        assert "1/3 solved" in content
        
        # Check link generation
        assert "[A](http://cf/A)" in content
        assert "| B |" in content  # No link for B

def test_update_all(tmp_path):
    """Test updating all directories recursively."""
    root = str(tmp_path)
    
    # Create structure: Codeforces/123
    cf_dir = os.path.join(root, "Codeforces", "123")
    os.makedirs(cf_dir)
    with open(os.path.join(cf_dir, "A.cpp"), 'w') as f:
        f.write("/**\n * Problem: A\n * Status: AC\n */")

    # Patch ROOT_DIR since it's a global in the module initialized at import time
    # Patch PLATFORM_DIRS to only look at our mock Codeforces dir
    with patch('commands.update.ROOT_DIR', root), \
         patch('commands.update.PLATFORM_DIRS', ['Codeforces']), \
         patch('sys.argv', ['cptools-update', '--all']):
        
        update.run()
        
    assert os.path.exists(os.path.join(cf_dir, "info.md"))