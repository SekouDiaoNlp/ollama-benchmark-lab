"""
Unit tests for the PatchEngine using subprocess mocks.
"""

import pytest
from unittest.mock import MagicMock
from benchmark.runtime.patch_engine import PatchEngine

def test_apply_patch_success(mocker, tmp_path):
    """Test successful patch application."""
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = MagicMock(returncode=0)
    
    engine = PatchEngine()
    # Should not raise
    engine.apply_patch(tmp_path, "diff text")
    
    mock_run.assert_called_once()

def test_apply_patch_failure(mocker, tmp_path):
    """Test error handling when git apply fails."""
    import subprocess
    mock_run = mocker.patch("subprocess.run")
    mock_run.side_effect = subprocess.CalledProcessError(1, cmd=["git"], stderr=b"error")
    
    engine = PatchEngine()
    with pytest.raises(RuntimeError, match="Patch failed"):
        engine.apply_patch(tmp_path, "bad diff")

def test_apply_empty_patch(mocker, tmp_path):
    """Test that empty patches are skipped safely."""
    mock_run = mocker.patch("subprocess.run")
    
    engine = PatchEngine()
    engine.apply_patch(tmp_path, "")
    
    mock_run.assert_not_called()
