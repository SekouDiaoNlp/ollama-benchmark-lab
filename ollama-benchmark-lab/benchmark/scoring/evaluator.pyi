from benchmark.sandbox.pool import SandboxPool as SandboxPool
from dataclasses import dataclass as dataclass
from typing import Any

class RealEvaluator:
    def score(self, task: dict[str, Any], output: str) -> float: ...
