from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE_FILE = ROOT / "results" / "model_profile.json"


class ModelProfiler:

    def __init__(self):
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if PROFILE_FILE.exists():
            return json.loads(PROFILE_FILE.read_text())
        return {}

    def save(self):
        PROFILE_FILE.write_text(json.dumps(self.data, indent=2))

    def update(self, model: str, latency: float, success: bool, output_chars: int):
        if model not in self.data:
            self.data[model] = {
                "runs": 0,
                "total_latency": 0.0,
                "failures": 0,
                "total_output_chars": 0
            }

        m = self.data[model]
        m["runs"] += 1
        m["total_latency"] += latency
        m["total_output_chars"] += output_chars

        if not success:
            m["failures"] += 1

    def score(self, model: str) -> float:
        """
        Lower is better (fast + stable)
        """
        m = self.data.get(model)
        if not m or m["runs"] == 0:
            return float("inf")

        avg_latency = m["total_latency"] / m["runs"]
        failure_rate = m["failures"] / m["runs"]

        return avg_latency * (1.0 + failure_rate)

    def fastest_models(self, k: int = 2) -> list[str]:
        return sorted(self.data.keys(), key=self.score)[:k]