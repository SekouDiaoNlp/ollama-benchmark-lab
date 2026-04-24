import json
from pathlib import Path
import pytest


TASK_FILES = list(Path("tasks").rglob("*.json"))


@pytest.mark.parametrize("task_file", TASK_FILES)
def test_task_contract(task_file):
    task = json.loads(task_file.read_text())

    # ensure structure exists
    assert "tests" in task
    assert "execution" in task

    assert isinstance(task["tests"]["path"], str)
    assert isinstance(task["execution"]["entrypoint"], str)