"""
Unit tests for the CheckpointManager.
"""

import json
import pytest
from benchmark.checkpoint import CheckpointManager

def test_checkpoint_save_and_load(tmp_path):
    """Test saving to and loading from a checkpoint file."""
    state_file = tmp_path / "state.jsonl"
    
    manager = CheckpointManager(state_file)
    manager.save("k1", {"v": 1})
    manager.save("k2", {"v": 2})
    
    # New manager should load existing state
    manager2 = CheckpointManager(state_file)
    assert manager2.done("k1")
    assert manager2.done("k2")
    assert manager2.state["k1"] == {"v": 1}

def test_checkpoint_done(tmp_path):
    """Test checking for completion status."""
    manager = CheckpointManager(tmp_path / "state.jsonl")
    manager.save("finished-task", {"status": "ok"})
    
    assert manager.done("finished-task") is True
    assert manager.done("pending-task") is False

def test_checkpoint_invalid_json(tmp_path):
    """Test handling of corrupted checkpoint lines."""
    state_file = tmp_path / "corrupted.jsonl"
    state_file.write_text('{"key": "k1", "value": {"v": 1}}\ninvalid-json\n')
    
    # Manager should probably skip or raise depending on implementation
    # Currently _load() raises json.JSONDecodeError
    with pytest.raises(json.JSONDecodeError):
        CheckpointManager(state_file)
