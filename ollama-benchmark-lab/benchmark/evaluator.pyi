from benchmark.sandbox.pool import SandboxPool as SandboxPool
from dataclasses import dataclass
from typing import Any

def normalize_text(text: str) -> str: ...
def is_valid_python(code: str) -> bool: ...
def has_function(code: str, name: str) -> bool: ...

@dataclass
class ScoreBreakdown:
    final: float
    exact_match: float
    containment: float
    structure: float
    validity: float

class RealEvaluator:
    def score(self, task: dict[str, Any], output: str) -> float: ...
