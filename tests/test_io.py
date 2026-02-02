"""
Tests for lib/io.py - IO and logging utilities.
"""
from lib.io import Colors, log, out, error, success, warning, info, header, bold

def test_colors_exist():
    """Ensure Color constants are defined."""
    assert Colors.HEADER
    assert Colors.FAIL
    assert Colors.ENDC
    assert Colors.GREEN
    assert Colors.WARNING
    assert Colors.BLUE
    assert Colors.BOLD

def test_log(capsys):
    """Test log prints to stderr."""
    log("test message")
    captured = capsys.readouterr()
    assert "test message" in captured.err
    assert captured.out == ""

def test_out(capsys):
    """Test out prints to stdout."""
    out("test output")
    captured = capsys.readouterr()
    assert "test output" in captured.out
    assert captured.err == ""

def test_error(capsys):
    """Test error prints to stderr with FAIL color."""
    error("failure")
    captured = capsys.readouterr()
    assert "failure" in captured.err
    assert Colors.FAIL in captured.err
    assert Colors.ENDC in captured.err

def test_success(capsys):
    """Test success prints to stderr with GREEN color."""
    success("great")
    captured = capsys.readouterr()
    assert "great" in captured.err
    assert Colors.GREEN in captured.err

def test_warning(capsys):
    """Test warning prints to stderr with WARNING color."""
    warning("careful")
    captured = capsys.readouterr()
    assert "careful" in captured.err
    assert Colors.WARNING in captured.err

def test_info(capsys):
    """Test info prints to stderr with BLUE color."""
    info("info")
    captured = capsys.readouterr()
    assert "info" in captured.err
    assert Colors.BLUE in captured.err

def test_header(capsys):
    """Test header prints to stderr with HEADER color."""
    header("HEAD")
    captured = capsys.readouterr()
    assert "HEAD" in captured.err
    assert Colors.HEADER in captured.err

def test_bold(capsys):
    """Test bold prints to stderr with BOLD color."""
    bold("bold text")
    captured = capsys.readouterr()
    assert "bold text" in captured.err
    assert Colors.BOLD in captured.err