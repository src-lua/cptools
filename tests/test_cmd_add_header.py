"""
Integration tests for commands/add_header.py
"""
import os
from unittest.mock import patch
from cptools.commands import add_header


def test_add_header_basic(tmp_path):
    """Test adding header to a file without one."""
    d = str(tmp_path)
    filepath = os.path.join(d, "test.cpp")

    # Create file without header
    with open(filepath, 'w') as f:
        f.write("#include <iostream>\nint main() { return 0; }\n")

    # Add header
    with patch('sys.argv', ['cptools-add-header', filepath]):
        add_header.run()

    # Verify header was added
    with open(filepath, 'r') as f:
        content = f.read()
        assert 'Author:' in content
        assert 'Problem:     test' in content
        assert 'Status:      ~' in content
        assert '#include <iostream>' in content


def test_add_header_with_options(tmp_path):
    """Test adding header with custom options."""
    d = str(tmp_path)
    filepath = os.path.join(d, "A.cpp")

    with open(filepath, 'w') as f:
        f.write("int main() {}\n")

    # Add header with options
    with patch('sys.argv', [
        'cptools-add-header', filepath,
        '--name', 'Two Sum',
        '--link', 'https://example.com/A',
        '--status', 'AC'
    ]):
        add_header.run()

    # Verify custom fields
    with open(filepath, 'r') as f:
        content = f.read()
        assert 'Problem:     A - Two Sum' in content
        assert 'Link:        https://example.com/A' in content
        assert 'Status:      AC' in content


def test_add_header_existing_header_no_force(tmp_path):
    """Test that existing header is not overwritten without --force."""
    d = str(tmp_path)
    filepath = os.path.join(d, "B.cpp")

    # Create file with header
    with open(filepath, 'w') as f:
        f.write("/**\n * Problem: B\n * Status: AC\n **/\nint main() {}\n")

    # Try to add header without force
    with patch('sys.argv', ['cptools-add-header', filepath]):
        add_header.run()

    # Verify original header is preserved
    with open(filepath, 'r') as f:
        content = f.read()
        # Should still have the original header with AC status
        assert content.count('Status:') == 1
        assert 'Status: AC' in content or 'Status:      AC' in content


def test_add_header_force_overwrite(tmp_path):
    """Test that --force overwrites existing header."""
    d = str(tmp_path)
    filepath = os.path.join(d, "C.cpp")

    # Create file with header
    with open(filepath, 'w') as f:
        f.write("/**\n * Problem: C\n * Status: AC\n **/\nint main() {}\n")

    # Add header with force
    with patch('sys.argv', ['cptools-add-header', filepath, '--force', '--status', 'WA']):
        add_header.run()

    # Verify new header was added
    with open(filepath, 'r') as f:
        content = f.read()
        assert 'Status:      WA' in content
        # Old header should be gone
        assert content.count('/**') == 1


def test_add_header_nonexistent_file(tmp_path):
    """Test error handling for nonexistent file."""
    d = str(tmp_path)
    filepath = os.path.join(d, "nonexistent.cpp")

    # Try to add header to nonexistent file
    with patch('sys.argv', ['cptools-add-header', filepath]):
        add_header.run()

    # File should not have been created
    assert not os.path.exists(filepath)


def test_add_header_preserves_code(tmp_path):
    """Test that existing code is preserved."""
    d = str(tmp_path)
    filepath = os.path.join(d, "code.cpp")

    original_code = """#include <bits/stdc++.h>
using namespace std;

int main() {
    cout << "Hello World" << endl;
    return 0;
}
"""

    with open(filepath, 'w') as f:
        f.write(original_code)

    # Add header
    with patch('sys.argv', ['cptools-add-header', filepath]):
        add_header.run()

    # Verify code is preserved
    with open(filepath, 'r') as f:
        content = f.read()
        # All original code should still be there
        assert '#include <bits/stdc++.h>' in content
        assert 'using namespace std;' in content
        assert 'cout << "Hello World"' in content
        # And header should be at the beginning
        assert content.startswith('/**')


def test_add_header_underscores_to_spaces(tmp_path):
    """Test that underscores in filename are converted to spaces in Problem field."""
    d = str(tmp_path)
    filepath = os.path.join(d, "word_other_word.cpp")

    with open(filepath, 'w') as f:
        f.write("int main() {}\n")

    # Add header
    with patch('sys.argv', ['cptools-add-header', filepath]):
        add_header.run()

    # Verify underscores are converted to spaces
    with open(filepath, 'r') as f:
        content = f.read()
        assert 'Problem:     word other word' in content
        assert 'word_other_word' not in content  # Underscores should not appear in header
