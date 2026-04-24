"""
Integration tests for the main benchmark runner workflow.
"""

import pytest
from unittest.mock import MagicMock
from benchmark.runner import BenchmarkRunner
from benchmark.checkpoint import CheckpointManager
from benchmark.ollama_client import OllamaClient
from benchmark.evaluator import RealEvaluator

def test_runner_complete_cycle(tmp_path):
    """Test a full run cycle with mocked components."""
    # Setup paths
    state_file = tmp_path / "state.jsonl"
    
    # Mock dependencies
    mock_client = MagicMock(spec=OllamaClient)
    mock_client.run.return_value = "generated code"
    
    mock_evaluator = MagicMock(spec=RealEvaluator)
    mock_evaluator.score.return_value = 1.0
    
    ckpt = CheckpointManager(state_file)
    
    runner = BenchmarkRunner(mock_client, mock_evaluator, ckpt)
    
    # Define tasks and models
    models = ["model-1"]
    tasks = [
        {"id": "t1", "prompt": "p1"},
        {"id": "t2", "prompt": "p2"}
    ]
    
    # Run
    runner.run(models, tasks, resume=False)
    
    # Verify
    assert mock_client.run.call_count == 2
    assert mock_evaluator.score.call_count == 2
    assert ckpt.done("model-1::t1")
    assert ckpt.done("model-1::t2")

def test_runner_resume_logic(tmp_path):
    """Test that resume skips already completed tasks."""
    state_file = tmp_path / "state.jsonl"
    ckpt = CheckpointManager(state_file)
    ckpt.save("m1::t1", {"score": 1.0})
    
    mock_client = MagicMock(spec=OllamaClient)
    mock_evaluator = MagicMock(spec=RealEvaluator)
    
    runner = BenchmarkRunner(mock_client, mock_evaluator, ckpt)
    
    models = ["m1"]
    tasks = [{"id": "t1"}, {"id": "t2"}]
    
    runner.run(models, tasks, resume=True)
    
    # Should only run t2
    assert mock_client.run.call_count == 1
    mock_client.run.assert_called_once_with(model="m1", prompt="")
