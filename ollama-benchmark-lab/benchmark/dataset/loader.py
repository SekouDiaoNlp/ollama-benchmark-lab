import json
from pathlib import Path

TASKS_DIR = Path("tasks")


def load_task_by_id(task_id: str):
    """
    Resolves task_id -> JSON task file
    """

    for f in TASKS_DIR.rglob("*.json"):
        data = json.loads(f.read_text())

        if data.get("id") == task_id or f.stem == task_id:
            return data

    raise FileNotFoundError(f"Task not found: {task_id}")