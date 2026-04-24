"""
Unit tests for the task loader.
"""

import json
import pytest
from pathlib import Path
from benchmark.dataset.loader import TaskLoader

def test_load_all_empty(tmp_path, monkeypatch):
    """Test loading from an empty tasks directory."""
    monkeypatch.setattr("benchmark.dataset.loader.TASKS_DIR", tmp_path)
    loader = TaskLoader()
    assert loader.load_all() == []

def test_load_all_with_files(tmp_path, monkeypatch):
    """Test loading multiple task files."""
    monkeypatch.setattr("benchmark.dataset.loader.TASKS_DIR", tmp_path)
    
    task1 = tmp_path / "task1.json"
    task1.write_text(json.dumps({"id": "t1", "val": 1}))
    
    # Nested task
    subdir = tmp_path / "sub"
    subdir.mkdir()
    task2 = subdir / "task2.json"
    task2.write_text(json.dumps({"id": "t2", "val": 2}))
    
    loader = TaskLoader()
    tasks = loader.load_all()
    
    assert len(tasks) == 2
    ids = {t["task_id"] for t in tasks}
    assert ids == {"t1", "t2"}

def test_load_by_id(tmp_path, monkeypatch):
    """Test loading a specific task by ID."""
    monkeypatch.setattr("benchmark.dataset.loader.TASKS_DIR", tmp_path)
    
    task_file = tmp_path / "my_task.json"
    task_file.write_text(json.dumps({"id": "real-id", "data": "foo"}))
    
    loader = TaskLoader()
    
    # Load by explicitly set ID
    assert loader.load_by_id("real-id")["task_id"] == "real-id"
    
    # Load by filename stem
    assert loader.load_by_id("my_task")["task_id"] == "my_task"

def test_load_by_id_not_found(tmp_path, monkeypatch):
    """Test error handling when task is missing."""
    monkeypatch.setattr("benchmark.dataset.loader.TASKS_DIR", tmp_path)
    loader = TaskLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_by_id("missing")
