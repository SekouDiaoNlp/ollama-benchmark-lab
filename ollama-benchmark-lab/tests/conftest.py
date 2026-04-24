"""
Shared pytest fixtures and configuration for the Ollama benchmark lab.
"""

import pytest
from unittest.mock import MagicMock
from pathlib import Path

@pytest.fixture
def mock_subprocess(mocker):
    """Fixture to mock subprocess.run and Popen."""
    mock_run = mocker.patch("subprocess.run")
    mock_popen = mocker.patch("subprocess.Popen")
    return mock_run, mock_popen

@pytest.fixture
def mock_docker(mocker):
    """Fixture to mock docker-py client."""
    mock_client = mocker.patch("docker.from_env")
    return mock_client

@pytest.fixture
def sample_task():
    """Fixture providing a valid sample task dictionary."""
    return {
        "id": "test-task-001",
        "repo_url": "https://github.com/example/repo",
        "commit": "abcdef123456",
        "mode": "SWE",
        "execution": {
            "entrypoint": "pytest -q"
        },
        "tests": {
            "path": "tests/test_logic.py"
        }
    }

@pytest.fixture
def temp_results_dir(tmp_path):
    """Fixture providing a temporary results directory."""
    results = tmp_path / "results"
    results.mkdir()
    return results
