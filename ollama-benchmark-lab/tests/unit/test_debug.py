"""
Unit tests for debug and path utilities.
"""

import pytest
from pathlib import Path
from benchmark.utils.debug import debug_path, ensure_path

def test_debug_path_output(capsys):
    """Test that debug_path prints the expected diagnostic info."""
    debug_path("test_var", "string_value")
    captured = capsys.readouterr()
    assert "[DEBUG PATH] test_var" in captured.out
    assert "TYPE: <class 'str'>" in captured.out
    assert "VALUE: string_value" in captured.out
    assert "WARNING: VALUE IS STRING" in captured.out

def test_ensure_path_conversion(capsys):
    """Test that ensure_path correctly converts strings to Path objects."""
    # From string
    p1 = ensure_path("/tmp/test", name="p1")
    assert isinstance(p1, Path)
    captured = capsys.readouterr()
    assert "WARNING" in captured.out  # Should log debug info
    
    # From Path
    p2 = Path("/tmp/test")
    p3 = ensure_path(p2)
    assert p3 is p2
    captured = capsys.readouterr()
    assert captured.out == ""  # Should not log anything
