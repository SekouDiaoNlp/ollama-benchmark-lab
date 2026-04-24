"""
Unit tests for the platform API.
"""

import pytest
from unittest.mock import MagicMock, patch
from benchmark.platform.api import BenchmarkPlatform, run_experiment

@patch("benchmark.platform.api.BenchmarkRunner")
@patch("benchmark.platform.api.load_tasks")
@patch("benchmark.platform.api.get_models")
def test_platform_run_experiment(mock_models, mock_tasks, mock_runner_class):
    """Test the BenchmarkPlatform orchestration."""
    mock_models.return_value = ["m1"]
    mock_tasks.return_value = [{"id": "t1"}, {"id": "t2"}]
    
    mock_runner = mock_runner_class.return_value
    
    platform = BenchmarkPlatform(limit=1)
    platform.run_experiment()
    
    # Runner should be called with limited tasks
    args = mock_runner.run.call_args
    assert len(args[0][1]) == 1  # tasks list
    assert args[1]["resume"] is False

def test_run_experiment_wrapper():
    """Test the run_experiment convenience wrapper."""
    with patch("benchmark.platform.api.BenchmarkPlatform") as mock_platform_class:
        mock_platform = mock_platform_class.return_value
        
        res = run_experiment(config={}, tasks=[{"id": "t1"}])
        
        assert res["passed"] is True
        mock_platform.run_experiment.assert_called_once()
        mock_platform_class.assert_called_once_with(limit=1)
