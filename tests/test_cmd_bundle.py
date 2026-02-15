"""
Integration tests for commands/bundle.py
"""
import os
import sys
from unittest.mock import patch
from cptools.commands import bundle
import pytest

def test_bundle_expands_includes(tmp_path):
    """Test that bundle expands local includes and keeps system includes."""
    d = str(tmp_path)

    # Create a library file
    lib_path = os.path.join(d, "lib.hpp")
    with open(lib_path, 'w') as f:
        f.write("// lib content\nvoid func() {}\n")

    # Create main file including the library
    main_path = os.path.join(d, "A.cpp")
    with open(main_path, 'w') as f:
        f.write('#include <iostream>\n#include "lib.hpp"\nint main() { func(); }')

    # Mock config and clipboard
    # We mock copy_to_clipboard to verify the final output
    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=True) as mock_clip, \
         patch('sys.argv', ['cptools-bundle', 'A']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        assert mock_clip.called
        args = mock_clip.call_args[0]
        content = args[0]

        # System include should remain
        assert "#include <iostream>" in content
        # Local include should be replaced by content
        assert '#include "lib.hpp"' not in content
        assert '// lib content' in content
        assert 'void func() {}' in content


def test_bundle_missing_include(tmp_path):
    """Test handling of missing included files."""
    d = str(tmp_path)

    # Create main file with non-existent include
    main_path = os.path.join(d, "B.cpp")
    with open(main_path, 'w') as f:
        f.write('#include <vector>\n#include "nonexistent.hpp"\nint main() {}')

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=True) as mock_clip, \
         patch('sys.argv', ['cptools-bundle', 'B']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        content = mock_clip.call_args[0][0]
        # Missing include should be kept as-is
        assert '#include "nonexistent.hpp"' in content


def test_bundle_circular_includes(tmp_path):
    """Test detection and handling of circular includes."""
    d = str(tmp_path)

    # Create two files that include each other
    file1 = os.path.join(d, "file1.hpp")
    file2 = os.path.join(d, "file2.hpp")

    with open(file1, 'w') as f:
        f.write('#pragma once\n#include "file2.hpp"\nvoid func1() {}')
    with open(file2, 'w') as f:
        f.write('#pragma once\n#include "file1.hpp"\nvoid func2() {}')

    main_path = os.path.join(d, "C.cpp")
    with open(main_path, 'w') as f:
        f.write('#include "file1.hpp"\nint main() {}')

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=True) as mock_clip, \
         patch('sys.argv', ['cptools-bundle', 'C']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        content = mock_clip.call_args[0][0]
        # Should have both functions, no duplicates
        assert 'void func1() {}' in content
        assert 'void func2() {}' in content
        # #pragma once should be removed
        assert '#pragma once' not in content


def test_bundle_output_to_file(tmp_path):
    """Test bundling to output file with -o option."""
    d = str(tmp_path)

    main_path = os.path.join(d, "D.cpp")
    with open(main_path, 'w') as f:
        f.write('#include <vector>\nint main() {}')

    output_path = os.path.join(d, "output.cpp")

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('sys.argv', ['cptools-bundle', 'D', '-o', output_path]), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            content = f.read()
            assert '#include <vector>' in content
            assert 'int main() {}' in content


def test_bundle_inplace(tmp_path):
    """Test bundling in-place with -i option."""
    d = str(tmp_path)

    lib_path = os.path.join(d, "mylib.hpp")
    with open(lib_path, 'w') as f:
        f.write("void helper() {}")

    main_path = os.path.join(d, "E.cpp")
    with open(main_path, 'w') as f:
        f.write('#include "mylib.hpp"\nint main() { helper(); }')

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('sys.argv', ['cptools-bundle', 'E', '-i']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        # Original file should be overwritten
        with open(main_path, 'r') as f:
            content = f.read()
            assert 'void helper() {}' in content
            assert '#include "mylib.hpp"' not in content


def test_bundle_no_clipboard_fallback(tmp_path, capsys):
    """Test fallback to stdout when clipboard unavailable."""
    d = str(tmp_path)

    main_path = os.path.join(d, "F.cpp")
    with open(main_path, 'w') as f:
        f.write('#include <iostream>\nint main() {}')

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=False), \
         patch('sys.argv', ['cptools-bundle', 'F']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        captured = capsys.readouterr()
        # Code should be printed to stdout
        assert '#include <iostream>' in captured.out
        assert 'int main() {}' in captured.out
        # Warning should be in stderr
        assert 'Could not copy to clipboard' in captured.err


def test_bundle_deduplicate_system_includes(tmp_path):
    """Test deduplication of system includes."""
    d = str(tmp_path)

    lib1 = os.path.join(d, "lib1.hpp")
    with open(lib1, 'w') as f:
        f.write('#include <vector>\nvoid f1() {}')

    lib2 = os.path.join(d, "lib2.hpp")
    with open(lib2, 'w') as f:
        f.write('#include <vector>\nvoid f2() {}')

    main_path = os.path.join(d, "G.cpp")
    with open(main_path, 'w') as f:
        f.write('#include <vector>\n#include "lib1.hpp"\n#include "lib2.hpp"\nint main() {}')

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=True) as mock_clip, \
         patch('sys.argv', ['cptools-bundle', 'G']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        content = mock_clip.call_args[0][0]
        # Should have <vector> only once
        assert content.count('#include <vector>') == 1


def test_bundle_deduplicate_using_namespace(tmp_path):
    """Test deduplication of 'using namespace std;'."""
    d = str(tmp_path)

    lib1 = os.path.join(d, "a.hpp")
    with open(lib1, 'w') as f:
        f.write('using namespace std;\nvoid a() {}')

    lib2 = os.path.join(d, "b.hpp")
    with open(lib2, 'w') as f:
        f.write('using namespace std;\nvoid b() {}')

    main_path = os.path.join(d, "H.cpp")
    with open(main_path, 'w') as f:
        f.write('using namespace std;\n#include "a.hpp"\n#include "b.hpp"\nint main() {}')

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=True) as mock_clip, \
         patch('sys.argv', ['cptools-bundle', 'H']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        content = mock_clip.call_args[0][0]
        # Should have 'using namespace std;' only once
        assert content.count('using namespace std;') == 1


def test_bundle_pragma_once_removed(tmp_path):
    """Test that #pragma once is removed from bundled output."""
    d = str(tmp_path)

    lib = os.path.join(d, "pragma_lib.hpp")
    with open(lib, 'w') as f:
        f.write('#pragma once\nvoid pragma_func() {}')

    main_path = os.path.join(d, "I.cpp")
    with open(main_path, 'w') as f:
        f.write('#include "pragma_lib.hpp"\nint main() {}')

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=True) as mock_clip, \
         patch('sys.argv', ['cptools-bundle', 'I']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        content = mock_clip.call_args[0][0]
        assert '#pragma once' not in content
        assert 'void pragma_func() {}' in content


def test_bundle_debug_includes_preserved(tmp_path):
    """Test that debug includes are not expanded."""
    d = str(tmp_path)

    main_path = os.path.join(d, "J.cpp")
    with open(main_path, 'w') as f:
        f.write('#include "debug.h"\nint main() {}')

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=True) as mock_clip, \
         patch('sys.argv', ['cptools-bundle', 'J']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        content = mock_clip.call_args[0][0]
        # Debug includes should be kept as-is
        assert '#include "debug.h"' in content


def test_bundle_file_not_found(tmp_path):
    """Test error when source file doesn't exist."""
    d = str(tmp_path)

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('sys.argv', ['cptools-bundle', 'NonExistent']), \
         patch('os.getcwd', return_value=d):

        with pytest.raises(SystemExit) as exc_info:
            bundle.run()
        assert exc_info.value.code == 1


def test_bundle_with_include_paths(tmp_path):
    """Test bundling with -I include paths from config."""
    d = str(tmp_path)
    inc_dir = tmp_path / "include"
    inc_dir.mkdir()

    # Library in include directory
    lib = inc_dir / "external.hpp"
    lib.write_text("void external_func() {}")

    main_path = os.path.join(d, "K.cpp")
    with open(main_path, 'w') as f:
        f.write('#include "external.hpp"\nint main() {}')

    config = {'compiler_flags': [f'-I{str(inc_dir)}']}

    with patch('cptools.commands.bundle.load_config', return_value=config), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=True) as mock_clip, \
         patch('sys.argv', ['cptools-bundle', 'K']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        content = mock_clip.call_args[0][0]
        assert 'void external_func() {}' in content
        assert '#include "external.hpp"' not in content


def test_bundle_strips_block_comments_from_libs(tmp_path):
    """Test that block comments are stripped from library files."""
    d = str(tmp_path)

    lib = os.path.join(d, "commented.hpp")
    with open(lib, 'w') as f:
        f.write('/* This is a comment */\nvoid func() {}\n/* Another comment */')

    main_path = os.path.join(d, "L.cpp")
    with open(main_path, 'w') as f:
        f.write('#include "commented.hpp"\nint main() {}')

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=True) as mock_clip, \
         patch('sys.argv', ['cptools-bundle', 'L']), \
         patch('os.getcwd', return_value=d):

        bundle.run()

        content = mock_clip.call_args[0][0]
        # Block comments from lib should be stripped
        assert '/* This is a comment */' not in content
        assert 'void func() {}' in content


def test_bundle_with_cpp_extension(tmp_path):
    """Test bundling when problem name has .cpp extension."""
    d = str(tmp_path)

    main_path = os.path.join(d, "M.cpp")
    with open(main_path, 'w') as f:
        f.write('#include <map>\nint main() {}')

    with patch('cptools.commands.bundle.load_config', return_value={'compiler_flags': []}), \
         patch('cptools.commands.bundle.copy_to_clipboard', return_value=True), \
         patch('sys.argv', ['cptools-bundle', 'M.cpp']), \
         patch('os.getcwd', return_value=d):

        bundle.run()
        # Should not throw error
