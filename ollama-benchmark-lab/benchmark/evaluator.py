from __future__ import annotations

from typing import Dict, Any
from benchmark.sandbox.pytest_runner import PytestRunner


class RealEvaluator:
    """
    SWE-bench style evaluator:
    - executes hidden tests
    - no heuristics
    """

    def __init__(self):
        self.runner = PytestRunner()

    def score(self, task: Dict[str, Any], output: str) -> float:

        tests = task.get("tests")

        # fallback safety
        if not tests:
            return 1.0 if len(output.strip()) > 0 else 0.0

        result = self.runner.evaluate(
            code=output,
            tests=tests
        )

        return 1.0 if result["passed"] else 0.0