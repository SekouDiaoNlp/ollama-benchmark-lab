"""
Dataset loader and normalization logic for SWE-bench formats.

This module provides the SWEBenchLoader class, which reads benchmark configurations
from JSON files and strictly normalizes them into the canonical task payload schema.

Example:
    >>> loader = SWEBenchLoader("data/tasks/")
    >>> tasks = loader.load_all()
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union


class SWEBenchLoader:
    """
    Loads SWE-bench style datasets with strict schema normalization.

    Attributes:
        dataset_path (Path): The resolved directory path containing the dataset JSONs.
    """

    def __init__(self, dataset_path: Union[str, Path]) -> None:
        """
        Initialize the loader with a target dataset path.

        Args:
            dataset_path (Union[str, Path]): Path to the dataset directory.
        """
        self.dataset_path: Path = Path(dataset_path)

    def load_all(self) -> List[Dict[str, Any]]:
        """
        Iterate through all JSON files in the dataset directory and normalize them.

        Returns:
            List[Dict[str, Any]]: A list of canonical task dictionaries.
        """
        tasks: List[Dict[str, Any]] = []

        for file in self.dataset_path.rglob("*.json"):
            task: Dict[str, Any] = json.loads(file.read_text())
            normalized_task: Dict[str, Any] = self._normalize(task)
            tasks.append(normalized_task)

        return tasks

    def _normalize(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce the SWE-bench canonical payload structure.

        This method sanitizes and sets defaults for execution endpoints and tests
        to ensure downstream engines do not fail on missing keys.

        Args:
            task (Dict[str, Any]): The raw dictionary loaded from JSON.

        Returns:
            Dict[str, Any]: The strictly structured task configuration.

        Raises:
            KeyError: If 'repo' or 'base_commit' are missing in the raw payload.
        """
        tests: Any = task.get("tests", {})
        tests_path: Any = tests.get("path") if isinstance(tests, dict) else None

        execution: Any = task.get("execution", {})
        entrypoint: str = "pytest -q"
        if isinstance(execution, dict):
            entrypoint = execution.get("entrypoint", "pytest -q")

        return {
            "id": task.get("id"),
            "repo": task["repo"],  # Enforces Key presence
            "base_commit": task["base_commit"],  # Enforces Key presence
            "patch": task.get("patch"),
            "tests": {
                "path": tests_path
            },
            "execution": {
                "entrypoint": entrypoint
            }
        }