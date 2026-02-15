"""
Integration tests for commands/new.py
"""
import os
from unittest.mock import patch, MagicMock
from cptools.commands import new

def test_create_contest_from_url(tmp_path):
    """Test creating a contest from a URL."""
    root_dir = str(tmp_path)
    template_path = os.path.join(root_dir, 'template.cpp')
    with open(template_path, 'w') as f:
        f.write("template")

    mock_info = {
        'platform': 'Codeforces',
        'contest_id': '1234',
        'base_url': 'https://codeforces.com/contest/1234/problem/{char}',
        'default_range': 'A~E'
    }

    with patch('cptools.commands.new.load_config', return_value={'author': 'TestUser'}), \
         patch('cptools.commands.new.ROOT_DIR', root_dir), \
         patch('cptools.commands.new.TEMPLATE_PATH', template_path), \
         patch('cptools.commands.new.parse_contest_url', return_value=mock_info), \
         patch('cptools.commands.new.get_input', side_effect=['1234', 'A~B']), \
         patch('cptools.commands.new.detect_judge') as mock_detect, \
         patch('cptools.commands.update.generate_info_md') as mock_gen_md:
        
        # Mock judge returning problem names
        mock_judge = MagicMock()
        mock_judge.fetch_contest_problems.return_value = {'A': 'Prob A', 'B': 'Prob B'}
        mock_detect.return_value = mock_judge

        new.create_contest_from_url("https://codeforces.com/contest/1234")

        contest_dir = os.path.join(root_dir, "Codeforces", "1234")
        assert os.path.exists(contest_dir)
        assert os.path.exists(os.path.join(contest_dir, "A.cpp"))
        assert os.path.exists(os.path.join(contest_dir, "B.cpp"))
        
        # Check content of A.cpp
        with open(os.path.join(contest_dir, "A.cpp"), 'r') as f:
            content = f.read()
            assert "Problem:     A - Prob A" in content
            assert "Link:        https://codeforces.com/contest/1234/problem/A" in content

        mock_gen_md.assert_called_once()