"""
Unit tests for task schema validation.
"""

import pytest
from benchmark.dataset.swe_schema import SWETask

def test_valid_swe_task():
    """Test valid SWETask instantiation and validation."""
    task = SWETask(
        task_id="task-1",
        repo_url="https://github.com/foo/bar",
        commit="1234567890abcdef"
    )
    task.validate()  # Should not raise

def test_invalid_repo_url():
    """Test validation failure for invalid URL scheme."""
    task = SWETask(
        task_id="task-1",
        repo_url="http://insecure.com",
        commit="123456"
    )
    with pytest.raises(AssertionError, match="repo_url must use HTTPS"):
        task.validate()

def test_invalid_commit_hash():
    """Test validation failure for too short commit hash."""
    task = SWETask(
        task_id="task-1",
        repo_url="https://github.com/foo/bar",
        commit="123"
    )
    with pytest.raises(AssertionError, match="commit hash must be at least 6 characters"):
        task.validate()
