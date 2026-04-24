from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List


ROOT = Path(__file__).resolve().parents[1]
CACHE_FILE = ROOT / "results" / "model_profile_cache.json"


class ModelProfiler:
    """
    Tracks runtime performance of models across benchmark runs.
    """

    def __init__(self):
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if not CACHE_FILE.exists():
            return {}
        try:
            return json.loads(CACHE_FILE.read_text())
        except Exception:
            return {}

    def save(self):
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(self.data, indent=2))

    def update(self, model: str, latency: float, success: bool):
        if model not in self.data:
            self.data[model] = {
                "runs": 0,
                "avg_latency": 0.0,
                "success_rate": 0.0
            }

        entry = self.data[model]

        # update running average latency
        n = entry["runs"]
        entry["avg_latency"] = (entry["avg_latency"] * n + latency) / (n + 1)

        # update success rate
        entry["success_rate"] = (
            (entry["success_rate"] * n + (1 if success else 0)) / (n + 1)
        )

        entry["runs"] += 1

        self.save()

    def get_fastest_models(self, models: List[str], k: int = 2) -> List[str]:
        """
        Returns fastest models based on cached average latency.
        Falls back gracefully if no data exists.
        """

        scored = []
        for m in models:
            if m in self.data:
                scored.append((m, self.data[m]["avg_latency"]))
            else:
                # unknown model = penalize slightly
                scored.append((m, 9999.0))

        scored.sort(key=lambda x: x[1])

        return [m for m, _ in scored[:k]]