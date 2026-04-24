"""
Nested evaluator using persistent SandboxPool.

This module provides the RealEvaluator logic for scoring ACT, PLAN,
and SWE benchmarks using structural heuristics and Docker-based pytest runs.

Example:
    >>> evaluator = RealEvaluator()
    >>> res = evaluator.score({"mode": "ACT", "expected": "foo"}, "output")
"""

from typing import Dict, Any, Optional

from benchmark.sandbox.pool import SandboxPool


_pool = SandboxPool(size=4)


class RealEvaluator:
    """
    Evaluates raw benchmark outputs against expected outcomes or execution sandboxes.
    """

    def score(self, task: Dict[str, Any], output: str) -> float:
        """
        Score the LLM output against the given task configuration.

        Args:
            task (Dict[str, Any]): The benchmark task dictionary.
            output (str): The raw output string from the LLM.

        Returns:
            float: A score between 0.0 and 1.0.
        """
        mode: str = str(task.get("mode", "ACT"))

        if mode == "ACT":
            return self._score_act(task, output)

        if mode == "PLAN":
            return self._score_plan(task, output)

        if mode == "SWE":
            return self._score_swe(task, output)

        return self._fallback(output)

    def _score_act(self, task: Dict[str, Any], output: str) -> float:
        """Score based on text containment and exact matching."""
        expected: Optional[str] = task.get("expected")

        if not expected:
            return 0.5 if len(output.strip()) > 0 else 0.0

        o: str = output.strip().lower()
        e: str = expected.strip().lower()

        exact: float = 1.0 if o == e else 0.0
        contain: float = 1.0 if e in o else 0.0

        return 0.7 * exact + 0.3 * contain

    def _score_plan(self, task: Dict[str, Any], output: str) -> float:
        """Score based on structural heuristics."""
        score: float = 0.0

        if 200 <= len(output) <= 5000:
            score += 0.2

        keywords = ["def ", "class ", "import ", "return", "architecture"]
        hits: int = sum(1 for k in keywords if k in output.lower())
        score += min(hits / 5, 0.4)

        if len(output.splitlines()) > 5:
            score += 0.2

        if output.strip():
            score += 0.2

        return min(score, 1.0)

    def _score_swe(self, task: Dict[str, Any], output: str) -> float:
        """Score based on isolated execution of tests in a Docker sandbox."""
        sandbox = _pool.acquire()

        try:
            timeout: int = int(task.get("timeout", 120))
            result: str = sandbox.exec(
                ["bash", "-lc", "pytest -q --disable-warnings --maxfail=1"],
                timeout=timeout,
            )

            return 1.0 if "failed" not in result.lower() else 0.0

        finally:
            _pool.release(sandbox)

    def _fallback(self, output: str) -> float:
        """Fallback evaluation if mode is unknown."""
        return 1.0 if len(output.strip()) > 0 else 0.0