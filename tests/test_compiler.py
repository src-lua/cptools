"""
Tests for lib/compiler.py - C++ compilation utilities.
"""
import subprocess
from unittest.mock import patch, MagicMock
from lib.compiler import compile_cpp, compile_from_config, CompilationResult


def test_compile_cpp_success():
    """Test successful compilation command generation."""
    with patch('subprocess.run') as mock_run:
        # Mock successful execution
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        res = compile_cpp("test.cpp", "test")
        
        assert res.success
        assert res.binary_path == "test"
        assert res.stderr == ""
        
        # Verify default command structure
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ["g++", "-O2", "-std=c++17", "test.cpp", "-o", "test"]


def test_compile_cpp_failure():
    """Test compilation failure handling."""
    with patch('subprocess.run') as mock_run:
        # Mock failed execution
        mock_run.return_value = MagicMock(returncode=1, stderr="syntax error")
        
        res = compile_cpp("test.cpp", "test")
        
        assert not res.success
        assert res.binary_path is None
        assert res.stderr == "syntax error"


def test_compile_cpp_custom_flags():
    """Test compilation with custom compiler and flags."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        compile_cpp("test.cpp", "test", compiler="clang++", flags=["-Wall", "-g"])
        
        args = mock_run.call_args[0][0]
        assert args == ["clang++", "-Wall", "-g", "test.cpp", "-o", "test"]


def test_compile_from_config():
    """Test compilation using configuration dictionary."""
    config = {
        "compiler": "clang++",
        "compiler_flags": ["-O3"]
    }
    with patch('lib.compiler.compile_cpp') as mock_compile:
        compile_from_config("test.cpp", "test", config)
        
        mock_compile.assert_called_with(
            "test.cpp", "test", compiler="clang++", flags=["-O3"]
        )


def test_compile_from_config_defaults():
    """Test compilation from config falls back to defaults."""
    config = {}  # Empty config
    with patch('lib.compiler.compile_cpp') as mock_compile:
        compile_from_config("test.cpp", "test", config)
        
        # Should use defaults defined in compile_from_config/compile_cpp logic
        mock_compile.assert_called_with(
            "test.cpp", "test", compiler="g++", flags=["-O2", "-std=c++17"]
        )