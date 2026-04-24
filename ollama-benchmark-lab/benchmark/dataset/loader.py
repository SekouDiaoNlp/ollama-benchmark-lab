"""
General task loader for SWE-style datasets.

This module provides the TaskLoader class for loading task definitions
from local JSON files.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

TASKS_DIR = Path("tasks")

class TaskLoader:
    """
    Loads task definitions from the filesystem.
    """

    def load_all(self) -> List[Dict[str, Any]]:
        """
        Load all task JSON files from the tasks directory.

        Returns:
            List[Dict[str, Any]]: A list of task configurations.
        """
        tasks: List[Dict[str, Any]] = []

        if not TASKS_DIR.exists():
            return tasks

        for f in TASKS_DIR.rglob("*.json"):
            try:
                data: Dict[str, Any] = json.loads(f.read_text())
                data["task_id"] = data.get("id") or f.stem
                tasks.append(data)
            except Exception as e:
                print(f"[TaskLoader] skip {f}: {e}")

        return tasks

    def load_by_id(self, task_id: str) -> Dict[str, Any]:
        """
        Load a specific task by its identifier or filename.

        Args:
            task_id (str): The ID or filename stem of the task.

        Returns:
            Dict[str, Any]: The task configuration.

        Raises:
            FileNotFoundError: If the task cannot be found.
        """
        if TASKS_DIR.exists():
            for f in TASKS_DIR.rglob("*.json"):
                try:
                    data: Dict[str, Any] = json.loads(f.read_text())
                    if data.get("id") == task_id or f.stem == task_id:
                        data["task_id"] = task_id
                        return data
                except Exception:
                    continue

        raise FileNotFoundError(f"Task not found: {task_id}")