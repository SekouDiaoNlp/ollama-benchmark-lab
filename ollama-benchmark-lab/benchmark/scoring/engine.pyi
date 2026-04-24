from _typeshed import Incomplete
from dataclasses import dataclass
from typing import Any

@dataclass
class ScoreResult:
    score: float
    breakdown: dict[str, float]
    notes: str = ...

class ScoringEngine:
    def score(self, task: dict[str, Any], output: str) -> ScoreResult: ...

class ACTScorer:
    def score(self, task: dict[str, Any], output: str) -> ScoreResult: ...

class PlanScorer:
    REQUIRED_HINTS: Incomplete
    def score(self, task: dict[str, Any], output: str) -> ScoreResult: ...

def score_task(task: dict[str, Any], output: str) -> ScoreResult: ...
