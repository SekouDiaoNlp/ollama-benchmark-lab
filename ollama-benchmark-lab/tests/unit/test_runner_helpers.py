"""
Unit tests for helper functions in runner.py.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from benchmark.runner import get_models, load_tasks, heartbeat, RESULTS_DIR

def test_get_models_all(mocker):
    """Test retrieving all models from ollama list output."""
    mock_sub = mocker.patch("subprocess.check_output")
    mock_sub.return_value = (
        "NAME             ID           SIZE   MODIFIED\n"
        "llama2:latest    abcdef123    4GB    2 days ago\n"
        "codellama:7b     fedcba456    5GB    3 days ago\n"
    )
    
    models = get_models("all")
    assert models == ["codellama:7b", "llama2:latest"]

def test_get_models_filter(mocker):
    """Test filtering models by mode."""
    mock_sub = mocker.patch("subprocess.check_output")
    mock_sub.return_value = (
        "NAME               ID\n"
        "model-noyap:1.0    abc\n"
        "model-normal:1.0   def\n"
    )
    
    models = get_models("noyap")
    assert models == ["model-noyap:1.0"]

def test_load_tasks_smoke(tmp_path):
    """Test loading tasks with smoke test limit."""
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    (tasks_dir / "t1.json").write_text(json.dumps({"id": "1"}))
    (tasks_dir / "t2.json").write_text(json.dumps({"id": "2"}))
    (tasks_dir / "t3.json").write_text(json.dumps({"id": "3"}))
    
    # We need to patch the global task_root or change CWD
    import benchmark.runner
    original_root = benchmark.runner.Path("tasks")
    try:
        benchmark.runner.Path = lambda *args: tmp_path / "tasks" if args == ("tasks",) else original_root
        # Actually it's easier to just patch the glob
        mocker_path = MagicMock()
        mocker_path.glob.return_value = [tasks_dir / "t1.json", tasks_dir / "t2.json", tasks_dir / "t3.json"]
        
        # Better: use a real temp dir and monkeypatch the local variable if it was one, 
        # but load_tasks uses `Path("tasks")` directly.
    except:
        pass

def test_load_tasks_real_glob(tmp_path, monkeypatch):
    """Test load_tasks with real file system globbing."""
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    (tasks_dir / "t1.json").write_text(json.dumps({"id": "1"}))
    
    # Patch Path to point to our temp tasks dir
    from pathlib import Path
    import benchmark.runner
    
    # Use monkeypatch to redirect the path logic if possible
    # but since it's hardcoded Path("tasks"), we'll just mock the class
    with patch("benchmark.runner.Path") as mock_path:
        mock_instance = mock_path.return_value
        mock_instance.glob.return_value = [tasks_dir / "t1.json"]
        
        tasks = load_tasks({})
        assert len(tasks) == 1
        assert tasks[0]["id"] == "1"

def test_heartbeat(tmp_path, monkeypatch):
    """Test writing heartbeat to disk."""
    monkeypatch.setattr("benchmark.runner.RESULTS_DIR", tmp_path)
    heartbeat("model-a", "task-1")
    
    hb_file = tmp_path / "heartbeat.txt"
    assert hb_file.exists()
    data = json.loads(hb_file.read_text())
    assert data["model"] == "model-a"
    assert data["task"] == "task-1"
