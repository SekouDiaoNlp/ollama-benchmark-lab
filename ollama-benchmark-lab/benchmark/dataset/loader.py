import json
from pathlib import Path

TASKS_DIR = Path("tasks")


class TaskLoader:
    """
    SWE-style dataset loader (batch + single-task support)
    """

    def load_all(self) -> list[dict]:
        tasks = []

        for f in TASKS_DIR.rglob("*.json"):
            try:
                data = json.loads(f.read_text())
                data["task_id"] = data.get("id") or f.stem
                tasks.append(data)
            except Exception as e:
                print(f"[TaskLoader] skip {f}: {e}")

        return tasks

    def load_by_id(self, task_id: str):
        for f in TASKS_DIR.rglob("*.json"):
            data = json.loads(f.read_text())

            if data.get("id") == task_id or f.stem == task_id:
                data["task_id"] = task_id
                return data

        raise FileNotFoundError(f"Task not found: {task_id}")