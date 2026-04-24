"""
Checkpoint management for the benchmarking process.

This module provides the CheckpointManager class, responsible for persisting
and loading the execution state of benchmark tasks to ensure continuity and
resume capabilities.

Example:
    >>> from pathlib import Path
    >>> manager = CheckpointManager(Path("state.jsonl"))
    >>> manager.save("task_123", {"status": "success"})
    >>> manager.done("task_123")
    True
"""

import json
from pathlib import Path
from typing import Any, Dict, Union


class CheckpointManager:
    """
    Manages state persistence for benchmark runs via a JSON Lines (jsonl) file.

    Attributes:
        path (Path): The file path where the checkpoint data is stored.
        state (Dict[str, Dict[str, Any]]): The in-memory cache of the checkpoint state.
    """

    def __init__(self, path: Union[Path, str]) -> None:
        """
        Initialize the CheckpointManager and load existing state if the file exists.

        Args:
            path (Union[Path, str]): The file system path to the state file.
        """
        self.path: Path = Path(path)
        self.state: Dict[str, Dict[str, Any]] = {}

        if self.path.exists():
            self._load()

    def _load(self) -> None:
        """
        Load the checkpoint state from the underlying JSON Lines file into memory.

        Raises:
            json.JSONDecodeError: If a line in the checkpoint file is not valid JSON.
        """
        for line in self.path.read_text().splitlines():
            obj: Dict[str, Any] = json.loads(line)
            key: str = obj["key"]
            value: Dict[str, Any] = obj["value"]
            self.state[key] = value

    def save(self, key: str, value: Dict[str, Any]) -> None:
        """
        Save a specific key-value pair to the checkpoint state.

        This updates both the in-memory cache and appends the serialized data
        to the underlying JSON Lines file.

        Args:
            key (str): The unique identifier for the state entry (e.g., task ID).
            value (Dict[str, Any]): The state data dictionary to store.
        """
        self.state[key] = value

        with self.path.open("a") as f:
            f.write(json.dumps({"key": key, "value": value}) + "\n")

    def done(self, key: str) -> bool:
        """
        Check whether a specific key exists in the checkpoint state.

        Args:
            key (str): The unique identifier to check.

        Returns:
            bool: True if the key exists in the state, False otherwise.
        """
        return key in self.state