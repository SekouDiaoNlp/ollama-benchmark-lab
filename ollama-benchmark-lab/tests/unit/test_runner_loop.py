"""
Unit tests for the BenchmarkRunner execution loop.
"""

import pytest
from unittest.mock import MagicMock, patch
from benchmark.runner import BenchmarkRunner

@patch("benchmark.runner.heartbeat")
def test_runner_error_in_task(mock_heartbeat, tmp_path):
    """Test that runner handles exceptions in individual tasks and continues."""
    mock_client = MagicMock()
    mock_client.run.side_effect = [Exception("Task 1 Failed"), "Task 2 Success"]
    
    mock_evaluator = MagicMock()
    mock_evaluator.score.return_value = 1.0
    
    mock_ckpt = MagicMock()
    mock_ckpt.done.return_value = False
    
    runner = BenchmarkRunner(mock_client, mock_evaluator, mock_ckpt)
    
    models = ["m1"]
    tasks = [{"id": "t1"}, {"id": "t2"}]
    
    # Should not raise exception
    runner.run(models, tasks, resume=False)
    
    # Verify both were attempted and saved (including error)
    assert mock_client.run.call_count == 2
    assert mock_ckpt.save.call_count == 2

def test_runner_initialization_with_defaults():
    """Test runner creation with default arguments."""
    mock_client = MagicMock()
    mock_evaluator = MagicMock()
    mock_ckpt = MagicMock()
    
    runner = BenchmarkRunner(mock_client, mock_evaluator, mock_ckpt)
    assert runner.client == mock_client
    assert runner.evaluator == mock_evaluator
