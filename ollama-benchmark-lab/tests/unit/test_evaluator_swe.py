"""
Unit tests for SWE scoring and pool interactions in evaluator.py.
"""

import pytest
from unittest.mock import MagicMock, patch
from benchmark.evaluator import RealEvaluator

@patch("benchmark.evaluator._pool")
def test_score_swe_pass(mock_pool):
    """Test SWE mode scoring when tests pass."""
    mock_sandbox = mock_pool.acquire.return_value
    mock_sandbox.exec.return_value = "collected 1 item / 0 failures / 1 passed"
    
    evaluator = RealEvaluator()
    task = {"mode": "SWE"}
    
    score = evaluator.score(task, "patch text")
    
    assert score == 1.0
    mock_pool.acquire.assert_called_once()
    mock_pool.release.assert_called_once_with(mock_sandbox)

@patch("benchmark.evaluator._pool")
def test_score_swe_fail(mock_pool):
    """Test SWE mode scoring when tests fail."""
    mock_sandbox = mock_pool.acquire.return_value
    mock_sandbox.exec.return_value = "FAILED tests/test_foo.py"
    
    evaluator = RealEvaluator()
    task = {"mode": "SWE"}
    
    score = evaluator.score(task, "patch text")
    
    assert score == 0.0

def test_score_plan_edge_cases():
    """Test PLAN mode with various output lengths and keywords."""
    evaluator = RealEvaluator()
    task = {"mode": "PLAN"}
    
    # Very short output
    assert evaluator.score(task, "too short") < 0.5
    
    # Rich output with keywords
    rich_output = "def implementation():\n    class Architecture:\n        import numpy\n        return True"
    score = evaluator.score(task, rich_output)
    assert score > 0.5
