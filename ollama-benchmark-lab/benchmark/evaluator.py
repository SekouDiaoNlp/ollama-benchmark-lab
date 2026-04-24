from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Dict, Any

from benchmark.sandbox.pool import SandboxPool


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_text(text: str) -> str:
    if text is None:
        return ""

    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


# =========================================================
# CODE VALIDATION
# =========================================================

def is_valid_python(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except Exception:
        return False


def has_function(code: str, name: str) -> bool:
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return True
        return False
    except Exception:
        return False


# =========================================================
# SCORE CORE
# =========================================================

@dataclass
class ScoreBreakdown:
    final: float
    exact_match: float
    containment: float
    structure: float
    validity: float


# =========================================================
# PERSISTENT SANDBOX POOL (GLOBAL)
# =========================================================

_pool = SandboxPool(size=4)
_pool.start()


# =========================================================
# REAL EVALUATOR
# =========================================================

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

    # =====================================================
    # ACT (light semantic matching)
    # =====================================================

    def _score_act(self, task: Dict[str, Any], output: str) -> float:
        expected = task.get("expected")

        if not expected:
            return 0.5 if len(output.strip()) > 0 else 0.0

        o = normalize_text(output)
        e = normalize_text(expected)

        exact = 1.0 if o == e else 0.0
        contain = 1.0 if e in o else 0.0

        return 0.7 * exact + 0.3 * contain

    # =====================================================
    # PLAN (structural heuristic retained)
    # =====================================================

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

    # =====================================================
    # SWE (REAL EXECUTION via persistent sandbox pool)
    # =====================================================

    def _score_swe(self, task: Dict[str, Any], output: str) -> float:
        """
        Executes model output in persistent Docker sandbox
        and runs pytest-based hidden tests.
        """

        sandbox = _pool.acquire()

        try:
            result = _pool.run(
                sandbox=sandbox,
                code=output,
                test_cmd="pytest -q --disable-warnings --maxfail=1",
                timeout=task.get("timeout", 120),
            )

            if not result["success"]:
                return 0.0

            # PASS / FAIL signal
            if result["returncode"] == 0:
                return 1.0

            # partial signal (optional debugging insight)
            stdout = result.get("stdout", "").lower()
            stderr = result.get("stderr", "").lower()

            if "failed" in stdout or "failed" in stderr:
                return 0.3

            return 0.0

        finally:
            _pool.release(sandbox)

    # =====================================================
    # FALLBACK
    # =====================================================

    def _fallback(self, output: str) -> float:
        return 1.0 if len(output.strip()) > 0 else 0.0