import hashlib
import json
from pathlib import Path


class ExecutionCache:
    """
    Deterministic caching layer for SWE-bench runs.
    """

    def __init__(self, root=".cache/executions"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _key(self, task: dict) -> str:
        raw = json.dumps(task, sort_keys=True).encode()
        return hashlib.sha256(raw).hexdigest()

    def exists(self, task: dict) -> bool:
        return (self.root / self._key(task)).exists()

    def load(self, task: dict):
        path = self.root / self._key(task)
        return json.loads(path.read_text())

    def save(self, task: dict, result: dict):
        path = self.root / self._key(task)
        path.write_text(json.dumps(result, indent=2))