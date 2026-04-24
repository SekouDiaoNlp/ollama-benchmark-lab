from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List


class DatasetVersioner:
    """
    Ensures reproducible benchmarking:
    - hashes tasks
    - generates manifest
    """

    def hash_task(self, task: Dict[str, Any]) -> str:
        payload = json.dumps(task, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()[:12]

    def build_manifest(self, tasks: List[Dict[str, Any]], out_path: str = "tasks/manifest.json"):

        manifest = {
            "version": "swe-bench-v2",
            "task_count": len(tasks),
            "tasks": []
        }

        for t in tasks:
            manifest["tasks"].append({
                "id": t.get("id"),
                "hash": self.hash_task(t),
                "mode": t.get("mode")
            })

        Path(out_path).write_text(json.dumps(manifest, indent=2))

        return manifest