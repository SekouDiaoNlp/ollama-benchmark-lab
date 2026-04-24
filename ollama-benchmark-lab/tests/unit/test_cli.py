"""
Unit tests for the autollama CLI.
"""

import pytest
from unittest.mock import MagicMock, patch
from autollama.cli import main, load_tasks

def test_load_tasks_limit():
    """Test task loading with limit."""
    tasks = load_tasks(limit=5)
    # The current mock implementation only has 1 sample task
    assert len(tasks) <= 1 

@patch("autollama.cli.run_experiment")
@patch("autollama.cli.console")
@patch("argparse.ArgumentParser.parse_args")
def test_cli_main_success(mock_args, mock_console, mock_run_exp):
    """Test successful CLI execution path."""
    mock_args.return_value = MagicMock(limit=1)
    mock_run_exp.return_value = {"passed": True}
    
    main()
    
    mock_run_exp.assert_called_once()
    mock_console.success.assert_any_call("TASK PASSED")

@patch("autollama.cli.run_experiment")
@patch("autollama.cli.console")
@patch("argparse.ArgumentParser.parse_args")
def test_cli_main_failure(mock_args, mock_console, mock_run_exp):
    """Test CLI execution path when experiment fails."""
    mock_args.return_value = MagicMock(limit=1)
    mock_run_exp.return_value = {"passed": False}
    
    main()
    
    mock_console.warn.assert_any_call("TASK FAILED")

@patch("autollama.cli.run_experiment")
@patch("autollama.cli.console")
@patch("argparse.ArgumentParser.parse_args")
def test_cli_main_exception(mock_args, mock_console, mock_run_exp):
    """Test CLI error handling when an exception occurs."""
    mock_args.return_value = MagicMock(limit=1)
    mock_run_exp.side_effect = Exception("System Crash")
    
    main()
    
    mock_console.error.assert_called_with("System Crash")
