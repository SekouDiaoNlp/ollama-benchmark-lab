from dataclasses import dataclass
from typing import Dict, Any

from benchmark.sandbox.pool import SandboxPool


_pool = SandboxPool(size=4)


class RealEvaluator:

    def score(self, task: Dict[str, Any], output: str) -> float:
        mode = task.get("mode", "ACT")

        if mode == "ACT":
            return self._score_act(task, output)

        if mode == "PLAN":
            return self._score_plan(task, output)

        if mode == "SWE":
            return self._score_swe(task, output)

        return self._fallback(output)

    def _score_act(self, task: Dict[str, Any], output: str) -> float:
        expected = task.get("expected")

        if not expected:
            return 0.5 if len(output.strip()) > 0 else 0.0

        o = output.strip().lower()
        e = expected.strip().lower()

        exact = 1.0 if o == e else 0.0
        contain = 1.0 if e in o else 0.0

        return 0.7 * exact + 0.3 * contain

    def _score_plan(self, task: Dict[str, Any], output: str) -> float:
        score = 0.0

        if 200 <= len(output) <= 5000:
            score += 0.2

        keywords = ["def ", "class ", "import ", "return", "architecture"]
        hits = sum(1 for k in keywords if k in output.lower())
        score += min(hits / 5, 0.4)

        if len(output.splitlines()) > 5:
            score += 0.2

        if output.strip():
            score += 0.2

        return min(score, 1.0)

    def _score_swe(self, task: Dict[str, Any], output: str) -> float:
        sandbox = _pool.acquire()

        try:
            result = sandbox.exec(
                ["bash", "-lc", "pytest -q --disable-warnings --maxfail=1"],
                timeout=task.get("timeout", 120),
            )

            return 1.0 if "failed" not in result.lower() else 0.0

        finally:
            _pool.release(sandbox)

    def _fallback(self, output: str) -> float:
        return 1.0 if len(output.strip()) > 0 else 0.0