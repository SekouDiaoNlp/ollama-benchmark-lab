"""
Regression tests for benchmark task schema compliance.

This module uses pytest to verify that all task JSON files in the tasks/
directory adhere to the required structural contract.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import pytest

# Discover all task files
TASK_FILES: List[Path] = list(Path("tasks").rglob("*.json"))

@pytest.mark.parametrize("task_file", TASK_FILES)
def test_task_contract(task_file: Path) -> None:
    """
    Verify the structural integrity of a single task JSON file.

    Args:
        task_file (Path): The path to the task file.
    """
    task: Dict[str, Any] = json.loads(task_file.read_text())

    # ensure structure exists
    assert "tests" in task, f"Missing 'tests' key in {task_file}"
    assert "execution" in task, f"Missing 'execution' key in {task_file}"

    tests_block: Any = task["tests"]
    assert isinstance(tests_block, dict), f"'tests' must be a dict in {task_file}"
    assert isinstance(tests_block.get("path"), str), f"'tests.path' must be a string in {task_file}"

    exec_block: Any = task["execution"]
    assert isinstance(exec_block, dict), f"'execution' must be a dict in {task_file}"
    assert isinstance(exec_block.get("entrypoint"), str), f"'execution.entrypoint' must be a string in {task_file}"