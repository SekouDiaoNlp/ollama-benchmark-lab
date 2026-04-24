"""
Dataset version control system.

This module provides the DatasetVersionControl class for creating
and loading immutable snapshots of datasets.
"""

import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any

class DatasetVersionControl:
    """
    Provides snapshot-based versioning for benchmark datasets.
    """

    def __init__(self, root: str = "dataset_versions") -> None:
        """
        Initialize the version control system.

        Args:
            root (str): Directory where snapshots will be stored.
        """
        self.root: Path = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _hash(self, data: Dict[str, Any]) -> str:
        """
        Generate a deterministic hash for a dataset.

        Args:
            data (Dict[str, Any]): The data to hash.

        Returns:
            str: The SHA-256 hex digest.
        """
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()

    def save_snapshot(self, dataset: List[Dict[str, Any]]) -> str:
        """
        Save a snapshot of the current dataset.

        Args:
            dataset (List[Dict[str, Any]]): The list of tasks to snapshot.

        Returns:
            str: The unique snapshot identifier.
        """
        snapshot_id = self._hash({"dataset": dataset})

        path = self.root / f"{snapshot_id}.json"
        path.write_text(json.dumps(dataset, indent=2))

        return snapshot_id

    def load_snapshot(self, snapshot_id: str) -> List[Dict[str, Any]]:
        """
        Load a previously saved dataset snapshot.

        Args:
            snapshot_id (str): The identifier of the snapshot.

        Returns:
            List[Dict[str, Any]]: The loaded dataset.

        Raises:
            FileNotFoundError: If the snapshot does not exist.
        """
        path = self.root / f"{snapshot_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_id}")
        
        data: List[Dict[str, Any]] = json.loads(path.read_text())
        return data