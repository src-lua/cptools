"""
C++ compilation utilities.

This module provides a clean interface for compiling C++ source files
with configurable compilers and flags.
"""
import subprocess
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CompilationResult:
    """Result of a compilation attempt."""
    success: bool
    stderr: str
    binary_path: Optional[str]
    command: List[str]


def compile_cpp(source, output, compiler="g++", flags=None):
    """
    Compile a C++ source file.

    Args:
        source: Path to .cpp file
        output: Path for output binary
        compiler: Compiler command (default: "g++")
        flags: Compiler flags (default: ["-O2", "-std=c++17"])

    Returns:
        CompilationResult with success status and details

    Examples:
        >>> result = compile_cpp("A.cpp", ".A")
        >>> if result.success:
        ...     print("Compilation successful!")
        ...     print(f"Binary: {result.binary_path}")
    """
    if flags is None:
        flags = ["-O2", "-std=c++17"]

    cmd = [compiler] + flags + [source, "-o", output]
    result = subprocess.run(cmd, capture_output=True, text=True)

    return CompilationResult(
        success=result.returncode == 0,
        stderr=result.stderr,
        binary_path=output if result.returncode == 0 else None,
        command=cmd
    )


def compile_from_config(source, output, config):
    """
    Compile using settings from config dict.

    Args:
        source: Path to .cpp file
        output: Path for output binary
        config: Config dict with 'compiler' and 'compiler_flags' keys

    Returns:
        CompilationResult

    Examples:
        >>> config = {"compiler": "g++", "compiler_flags": ["-O2", "-std=c++20"]}
        >>> result = compile_from_config("A.cpp", ".A", config)
    """
    return compile_cpp(
        source,
        output,
        compiler=config.get("compiler", "g++"),
        flags=config.get("compiler_flags", ["-O2", "-std=c++17"])
    )
