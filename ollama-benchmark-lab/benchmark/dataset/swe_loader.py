"""
SWE-bench specific dataset loader.

This module provides the SWEBenchLoader class for loading tasks
compatible with the SWE-bench format.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

class SWEBenchLoader:
    """
    Loads tasks requiring repo_url and commit (SWE-bench format).
    """

    def __init__(self, root: str = "tasks") -> None:
        """
        Initialize the loader with a root directory.

        Args:
            root (str): The directory containing task JSON files.
        """
        self.root: Path = Path(root)

    def load_all(self) -> List[Dict[str, Any]]:
        """
        Load all valid SWE-bench tasks from the root directory.

        Returns:
            List[Dict[str, Any]]: A list of task configurations.
        """
        tasks: List[Dict[str, Any]] = []

        if not self.root.exists():
            return tasks

        for f in self.root.rglob("*.json"):
            try:
                data: Dict[str, Any] = json.loads(f.read_text())

                # HARD REQUIREMENTS (SWE-bench mode)
                if "repo_url" not in data or "commit" not in data:
                    continue

                data["task_id"] = data.get("task_id") or f.stem
                tasks.append(data)
            except Exception:
                continue

        return tasks