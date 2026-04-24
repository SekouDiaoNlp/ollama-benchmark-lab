import json
from pathlib import Path


class DatasetLoader:
    """
    SWE-bench style dataset resolver.

    Converts logical task IDs into physical file paths.
    """

    def __init__(self, root: Path):
        self.root = root
        self.tasks_dir = root / "tasks"

    def list_tasks(self):
        """Return all task JSON files."""
        return list(self.tasks_dir.rglob("*.json"))

    def load_task(self, task_id: str):
        """
        Load a task by ID or filename stem.
        """
        for f in self.list_tasks():
            if f.stem == task_id or f.name == task_id:
                return json.loads(f.read_text())

        raise FileNotFoundError(f"Task not found: {task_id}")

    def resolve_path(self, task):
        """
        Extract path safely if needed for debugging/logging.
        """
        return task.get("__file__")