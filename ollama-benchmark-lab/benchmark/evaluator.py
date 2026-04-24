from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Dict, Any, Optional


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


class RealEvaluator:

    def score(self, task: Dict[str, Any], output: str) -> float:
        mode = task.get("mode", "ACT")
        prompt = task.get("prompt", "")

        if mode == "ACT":
            return self._score_act(task, output)

        if mode == "PLAN":
            return self._score_plan(task, output)

        if mode == "SWE":
            return self._score_swe(task, output)

        return self._fallback(output)

    # =====================================================
    # ACT: text correctness
    # =====================================================

    def _score_act(self, task: Dict[str, Any], output: str) -> float:
        expected = task.get("expected")

        if not expected:
            # weak supervision fallback
            return 0.5 if len(output.strip()) > 0 else 0.0

        o = normalize_text(output)
        e = normalize_text(expected)

        exact = 1.0 if o == e else 0.0
        contain = 1.0 if e in o else 0.0

        return 0.7 * exact + 0.3 * contain

    # =====================================================
    # PLAN: structural quality heuristic
    # =====================================================

    def _score_plan(self, task: Dict[str, Any], output: str) -> float:
        score = 0.0

        # length sanity
        if 200 <= len(output) <= 5000:
            score += 0.2

        # presence of structure markers
        structure_keywords = ["def ", "class ", "import ", "return", ":", "architecture"]
        hits = sum(1 for k in structure_keywords if k in output.lower())
        score += min(hits / 5, 0.4)

        # pseudo-coherence
        if len(output.splitlines()) > 5:
            score += 0.2

        # non-empty reward
        if output.strip():
            score += 0.2

        return min(score, 1.0)

    # =====================================================
    # SWE: code correctness approximation
    # =====================================================

    def _score_swe(self, task: Dict[str, Any], output: str) -> float:
        score = 0.0

        # validity
        valid = is_valid_python(output)
        score += 0.4 if valid else 0.0

        # structure
        if "def " in output:
            score += 0.2

        # test awareness
        if "pytest" in output or "assert" in output:
            score += 0.2

        # completeness
        if len(output.splitlines()) > 10:
            score += 0.2

        return min(score, 1.0)

    # =====================================================
    # fallback
    # =====================================================

    def _fallback(self, output: str) -> float:
        return 1.0 if len(output.strip()) > 0 else 0.0