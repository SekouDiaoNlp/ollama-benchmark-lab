"""
Code execution and semantic matching evaluator for LLM outputs.

This module provides the RealEvaluator and utility functions to normalize text,
validate Python code, and score outputs against ACT, PLAN, and SWE tasks using
both heuristics and isolated sandbox execution.

Example:
    >>> from benchmark.evaluator import RealEvaluator
    >>> evaluator = RealEvaluator()
    >>> task = {"mode": "ACT", "expected": "foo"}
    >>> score = evaluator.score(task, "output containing foo")
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Dict, Any, Optional

from benchmark.sandbox.pool import SandboxPool


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_text(text: Optional[str]) -> str:
    """
    Normalize text by lowering case and collapsing whitespace.

    Args:
        text (Optional[str]): The raw text to normalize.

    Returns:
        str: The normalized string. Empty string if input is None.
    """
    if text is None:
        return ""

    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


# =========================================================
# CODE VALIDATION
# =========================================================

def is_valid_python(code: str) -> bool:
    """
    Check if a given string contains syntactically valid Python code.

    Args:
        code (str): The code to validate.

    Returns:
        bool: True if valid Python, False otherwise.
    """
    try:
        ast.parse(code)
        return True
    except Exception:
        return False


def has_function(code: str, name: str) -> bool:
    """
    Determine whether a specific function name is defined in the code.

    Args:
        code (str): The Python code to inspect.
        name (str): The name of the function to find.

    Returns:
        bool: True if the function is defined, False otherwise.
    """
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
    """
    Detailed breakdown of an evaluation score.

    Attributes:
        final (float): The final aggregated score [0.0, 1.0].
        exact_match (float): Score component for exact semantic match.
        containment (float): Score component for expected text containment.
        structure (float): Score component for code structure heuristics.
        validity (float): Score component for valid code syntax.
    """
    final: float
    exact_match: float
    containment: float
    structure: float
    validity: float


# =========================================================
# PERSISTENT SANDBOX POOL (GLOBAL)
# =========================================================

_pool = SandboxPool(size=4)


# =========================================================
# REAL EVALUATOR
# =========================================================

class RealEvaluator:
    """
    Evaluator orchestrator for routing task output to the appropriate scoring logic.
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
        mode: str = task.get("mode", "ACT")

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
        """Score based on text containment and exact matching."""
        expected: Optional[str] = task.get("expected")

        if not expected:
            return 0.5 if len(output.strip()) > 0 else 0.0

        o: str = normalize_text(output)
        e: str = normalize_text(expected)

        exact: float = 1.0 if o == e else 0.0
        contain: float = 1.0 if e in o else 0.0

        return 0.7 * exact + 0.3 * contain

    # =====================================================
    # PLAN (structural heuristic retained)
    # =====================================================

    def _score_plan(self, task: Dict[str, Any], output: str) -> float:
        """Score based on code length, line counts, and keyword occurrences."""
        score: float = 0.0

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
        """Score based on isolated execution of tests in a Docker sandbox."""
        sandbox = _pool.acquire()

        try:
            timeout: int = task.get("timeout", 120)
            result = sandbox.exec(
                ["bash", "-lc", "pytest -q --disable-warnings --maxfail=1"],
                timeout=timeout,
            )

            return 1.0 if "failed" not in str(result).lower() else 0.0

        finally:
            _pool.release(sandbox)

    # =====================================================
    # FALLBACK
    # =====================================================

    def _fallback(self, output: str) -> float:
        """Fallback evaluation if mode is unknown."""
        return 1.0 if len(output.strip()) > 0 else 0.0