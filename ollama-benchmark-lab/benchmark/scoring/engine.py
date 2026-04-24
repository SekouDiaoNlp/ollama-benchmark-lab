"""
Modular scoring engine for benchmark outputs.

This module provides the core `ScoringEngine` and specialized scorers like
`ACTScorer` and `PlanScorer` to evaluate LLM outputs based on syntax,
runtime execution, and structural rubrics.

Example:
    >>> engine = ScoringEngine()
    >>> res = engine.score({"mode": "PLAN"}, "def test(): pass")
    >>> print(res.score)
"""

from __future__ import annotations

import ast
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Dict, Any, List


# =========================================================
# RESULT MODEL
# =========================================================

@dataclass
class ScoreResult:
    """
    Data structure representing the outcome of a scoring evaluation.

    Attributes:
        score (float): The final aggregated score [0.0, 1.0].
        breakdown (Dict[str, float]): The individual score components.
        notes (str): Human-readable notes or error traces regarding the score.
    """
    score: float
    breakdown: Dict[str, float]
    notes: str = ""


# =========================================================
# MAIN ENTRYPOINT
# =========================================================

class ScoringEngine:
    """
    Dispatcher engine to route task outputs to the appropriate scorer.
    """

    def score(self, task: Dict[str, Any], output: str) -> ScoreResult:
        """
        Evaluate the output based on the task's defined mode.

        Args:
            task (Dict[str, Any]): The benchmark task dictionary.
            output (str): The raw LLM generation string.

        Returns:
            ScoreResult: The detailed scoring breakdown.
        """
        mode: str = str(task.get("mode", ""))

        if mode == "ACT":
            return ACTScorer().score(task, output)

        if mode == "PLAN":
            return PlanScorer().score(task, output)

        return ScoreResult(0.0, {"error": 1.0}, "Unknown task mode")


# =========================================================
# ACT SCORING (EXECUTION-BASED)
# =========================================================

class ACTScorer:
    """
    Execution-based scorer for evaluating concrete actions.
    """

    def _extract_code(self, output: str) -> str:
        """
        Try to isolate Python code from model output.

        Args:
            output (str): Raw model output.

        Returns:
            str: The extracted code block or the raw output.
        """
        if "```" in output:
            blocks: List[str] = output.split("```")
            for b in blocks:
                if "def " in b or "class " in b:
                    return b.strip()
        return output

    def _run_code(self, code: str) -> subprocess.CompletedProcess[str]:
        """
        Executes code in isolated temp file.

        Args:
            code (str): Python source code to execute.

        Returns:
            subprocess.CompletedProcess[str]: The result of the subprocess execution.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path: str = f"{tmp}/solution.py"

            with open(path, "w") as f:
                f.write(code)

            return subprocess.run(
                ["python", path],
                capture_output=True,
                text=True,
                timeout=10
            )

    def score(self, task: Dict[str, Any], output: str) -> ScoreResult:
        """
        Score an ACT mode output by checking syntax and runtime validity.

        Args:
            task (Dict[str, Any]): The benchmark task payload.
            output (str): The raw output string.

        Returns:
            ScoreResult: The execution score result.
        """
        code: str = self._extract_code(output)

        breakdown: Dict[str, float] = {
            "syntax_ok": 0.0,
            "runtime_ok": 0.0,
            "test_pass": 0.0
        }

        # 1. syntax check
        try:
            ast.parse(code)
            breakdown["syntax_ok"] = 1.0
        except SyntaxError:
            return ScoreResult(0.0, breakdown, "Syntax error")

        # 2. runtime execution
        try:
            result = self._run_code(code)

            if result.returncode == 0:
                breakdown["runtime_ok"] = 1.0
            else:
                return ScoreResult(0.2, breakdown, result.stderr[:200])

        except Exception as e:
            return ScoreResult(0.1, breakdown, str(e))

        # 3. placeholder test signal (EXTENDABLE)
        breakdown["test_pass"] = 0.5

        score: float = sum(breakdown.values()) / len(breakdown)

        return ScoreResult(score, breakdown, "ACT execution-based score")


# =========================================================
# PLAN SCORING (RUBRIC + STRUCTURE)
# =========================================================

class PlanScorer:
    """
    Rubric-based heuristic scorer for planning outputs.
    """

    REQUIRED_HINTS: List[str] = [
        "class",
        "def",
        "type",
        "import",
    ]

    def score(self, task: Dict[str, Any], output: str) -> ScoreResult:
        """
        Score a PLAN mode output based on structural heuristics.

        Args:
            task (Dict[str, Any]): The benchmark task payload.
            output (str): The raw output string.

        Returns:
            ScoreResult: The heuristic score result.
        """
        breakdown: Dict[str, float] = {
            "structure": 0.0,
            "typing": 0.0,
            "completeness": 0.0
        }

        text: str = output.lower()

        # structure signal
        structure_hits: int = sum(1 for h in self.REQUIRED_HINTS if h in text)
        breakdown["structure"] = structure_hits / len(self.REQUIRED_HINTS)

        # typing hint
        breakdown["typing"] = 1.0 if "->" in output or "typing" in text else 0.5

        # completeness heuristic
        length: int = len(output)
        if length > 1500:
            breakdown["completeness"] = 1.0
        elif length > 800:
            breakdown["completeness"] = 0.7
        else:
            breakdown["completeness"] = 0.3

        score: float = sum(breakdown.values()) / len(breakdown)

        return ScoreResult(score, breakdown, "PLAN rubric score")


# =========================================================
# DISPATCHER
# =========================================================

def score_task(task: Dict[str, Any], output: str) -> ScoreResult:
    """
    Wrapper function to score a task using the ScoringEngine.

    Args:
        task (Dict[str, Any]): The benchmark task dictionary.
        output (str): The raw string output from the model.

    Returns:
        ScoreResult: The resulting score payload.
    """
    engine = ScoringEngine()
    return engine.score(task, output)