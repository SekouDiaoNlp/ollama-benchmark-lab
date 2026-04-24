import hashlib
import json
from pathlib import Path


class DatasetVersionControl:
    """
    Snapshot-based dataset versioning (Git-like semantics).
    """

    def __init__(self, root="dataset_versions"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _hash(self, data: dict) -> str:
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()

    def save_snapshot(self, dataset: list[dict]):
        snapshot_id = self._hash({"dataset": dataset})

        path = self.root / f"{snapshot_id}.json"
        path.write_text(json.dumps(dataset, indent=2))

        return snapshot_id

    def load_snapshot(self, snapshot_id: str):
        path = self.root / f"{snapshot_id}.json"
        return json.loads(path.read_text())