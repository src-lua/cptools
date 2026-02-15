"""
Integration tests for commands/add.py
"""
import os
from unittest.mock import patch, MagicMock
from cptools.commands import add

def test_add_from_name(tmp_path):
    """Test adding a problem by name."""
    d = str(tmp_path)
    
    # Create template
    template_path = os.path.join(d, "template.cpp")
    with open(template_path, 'w') as f:
        f.write("template code")
        
    with patch('cptools.commands.add.load_config', return_value={'author': 'Me'}), \
         patch('cptools.commands.add.TEMPLATE_PATH', template_path), \
         patch('sys.argv', ['cptools-add', 'A', d]):
         
        add.run()
        
        created_file = os.path.join(d, "A.cpp")
        assert os.path.exists(created_file)
        with open(created_file, 'r') as f:
            content = f.read()
            assert "Problem:     A" in content
            assert "Author:      Me" in content

def test_add_from_name_sibling_link(tmp_path):
    """Test adding problem inherits link from sibling."""
    d = str(tmp_path)
    
    # Create sibling A.cpp
    with open(os.path.join(d, "A.cpp"), 'w') as f:
        f.write("/**\n * Problem: A - Name\n * Link: http://link\n */")
        
    # Create template
    template_path = os.path.join(d, "template.cpp")
    with open(template_path, 'w') as f:
        f.write("template")

    with patch('cptools.commands.add.load_config', return_value={'author': 'Me'}), \
         patch('cptools.commands.add.TEMPLATE_PATH', template_path), \
         patch('sys.argv', ['cptools-add', 'A-brute', d]):
         
        add.run()
        
        created = os.path.join(d, "A-brute.cpp")
        assert os.path.exists(created)
        with open(created, 'r') as f:
            content = f.read()
            assert "Link:        http://link" in content
            assert "Problem:     A-brute - Name" in content

def test_add_from_url(tmp_path):
    """Test adding problem from URL."""
    root = str(tmp_path)
    
    # Mock template
    template_path = os.path.join(root, "template.cpp")
    with open(template_path, 'w') as f: f.write("template")
    
    # Mock parse_problem_url
    mock_info = {
        'platform_dir': 'Codeforces/1234',
        'filename': 'A',
        'letter': 'A',
        'contest_id': '1234',
        'link': 'http://cf/1234/A'
    }
    
    with patch('cptools.commands.add.load_config', return_value={'author': 'Me'}), \
         patch('cptools.commands.add.get_repo_root', return_value=root), \
         patch('cptools.commands.add.TEMPLATE_PATH', template_path), \
         patch('cptools.commands.add.parse_problem_url', return_value=mock_info), \
         patch('cptools.commands.add.detect_judge') as mock_detect, \
         patch('sys.argv', ['cptools-add', 'http://cf/1234/A']):
         
        # Mock judge returning problem name
        mock_judge = MagicMock()
        mock_judge.fetch_problem_name.return_value = "Problem Name"
        mock_detect.return_value = mock_judge
        
        add.run()
        
        dest_dir = os.path.join(root, "Codeforces/1234")
        dest_file = os.path.join(dest_dir, "A.cpp")
        
        assert os.path.exists(dest_file)
        with open(dest_file, 'r') as f:
            content = f.read()
            assert "Problem:     A - Problem Name" in content
            assert "Link:        http://cf/1234/A" in content