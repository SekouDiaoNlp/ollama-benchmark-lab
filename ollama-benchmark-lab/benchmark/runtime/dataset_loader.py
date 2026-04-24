"""
Dataset resolution and task loading for SWE-bench evaluations.

This module provides the DatasetLoader class, which maps logical task IDs
to physical JSON configuration files stored within the repository.

Example:
    >>> from pathlib import Path
    >>> loader = DatasetLoader(Path("/opt/benchmark"))
    >>> task = loader.load_task("task_001")
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class DatasetLoader:
    """
    SWE-bench style dataset resolver.

    Converts logical task IDs into physical file paths and loads their JSON contents.

    Attributes:
        root (Path): The root directory of the benchmark lab.
        tasks_dir (Path): The dedicated subdirectory containing task JSON files.
    """

    def __init__(self, root: Path) -> None:
        """
        Initialize the DatasetLoader.

        Args:
            root (Path): The base path of the project.
        """
        self.root: Path = root
        self.tasks_dir: Path = root / "tasks"

    def list_tasks(self) -> List[Path]:
        """
        Return all task JSON files located within the tasks directory.

        Returns:
            List[Path]: A list of file paths ending in .json.
        """
        return list(self.tasks_dir.rglob("*.json"))

    def load_task(self, task_id: str) -> Dict[str, Any]:
        """
        Load a task definition by its ID or filename stem.

        Args:
            task_id (str): The logical identifier or file stem of the task.

        Returns:
            Dict[str, Any]: The parsed JSON task payload.

        Raises:
            FileNotFoundError: If no task file matching the ID is found.
            json.JSONDecodeError: If the task file contains invalid JSON.
        """
        for f in self.list_tasks():
            if f.stem == task_id or f.name == task_id:
                content: Dict[str, Any] = json.loads(f.read_text())
                return content

        raise FileNotFoundError(f"Task not found: {task_id}")

    def resolve_path(self, task: Dict[str, Any]) -> Optional[str]:
        """
        Extract the internal file path from a task payload if available.

        Args:
            task (Dict[str, Any]): The task payload dictionary.

        Returns:
            Optional[str]: The internal file path if present, otherwise None.
        """
        result: Optional[str] = task.get("__file__")
        return result