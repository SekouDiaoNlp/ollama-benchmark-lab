"""
Unit tests for the console UI components.
"""

import pytest
from benchmark.ui.console import Console as UIConsole
from benchmark.utils.console import Console as UtilsConsole

def test_ui_console_methods(capsys):
    """Test all methods of the UI Console class."""
    UIConsole.ok("success")
    UIConsole.warn("warning")
    UIConsole.error("failure")
    UIConsole.info("info")
    
    captured = capsys.readouterr()
    assert "✔ success" in captured.out
    assert "⚠ warning" in captured.out
    assert "✖ failure" in captured.out
    assert "info" in captured.out

def test_utils_console_methods(capsys):
    """Test all methods of the Utils Console class."""
    console = UtilsConsole()
    console.info("info")
    console.success("success")
    console.warn("warning")
    console.error("error")
    console.step("step")
    
    captured = capsys.readouterr()
    assert "info" in captured.out
    assert "✔ success" in captured.out
    assert "⚠ warning" in captured.out
    assert "✖ error" in captured.out
    assert "→ step" in captured.out
