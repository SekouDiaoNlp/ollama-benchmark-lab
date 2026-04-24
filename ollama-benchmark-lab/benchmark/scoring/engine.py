from __future__ import annotations

import ast
import subprocess
import tempfile
import textwrap
from dataclasses import dataclass
from typing import Dict, Any


# =========================================================
# RESULT MODEL
# =========================================================

@dataclass
class ScoreResult:
    score: float
    breakdown: Dict[str, float]
    notes: str = ""


# =========================================================
# MAIN ENTRYPOINT
# =========================================================

class ScoringEngine:

    def score(self, task: Dict[str, Any], output: str) -> ScoreResult:
        mode = task.get("mode")

        if mode == "ACT":
            return self._score_act(task, output)

        if mode == "PLAN":
            return self._score_plan(task, output)

        return ScoreResult(0.0, {"error": 1.0}, "Unknown task mode")


# =========================================================
# ACT SCORING (EXECUTION-BASED)
# =========================================================

class ACTScorer:

    def _extract_code(self, output: str) -> str:
        """
        Try to isolate Python code from model output.
        """
        if "```" in output:
            blocks = output.split("```")
            for b in blocks:
                if "def " in b or "class " in b:
                    return b.strip()
        return output

    def _run_code(self, code: str) -> subprocess.CompletedProcess:
        """
        Executes code in isolated temp file.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = f"{tmp}/solution.py"

            with open(path, "w") as f:
                f.write(code)

            return subprocess.run(
                ["python", path],
                capture_output=True,
                text=True,
                timeout=10
            )

    def score(self, task: Dict[str, Any], output: str) -> ScoreResult:
        code = self._extract_code(output)

        breakdown = {
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
        # later: plug pytest harness per task
        breakdown["test_pass"] = 0.5

        score = sum(breakdown.values()) / len(breakdown)

        return ScoreResult(score, breakdown, "ACT execution-based score")


# =========================================================
# PLAN SCORING (RUBRIC + STRUCTURE)
# =========================================================

class PlanScorer:

    REQUIRED_HINTS = [
        "class",
        "def",
        "type",
        "import",
    ]

    def score(self, task: Dict[str, Any], output: str) -> ScoreResult:

        breakdown = {
            "structure": 0.0,
            "typing": 0.0,
            "completeness": 0.0
        }

        text = output.lower()

        # structure signal
        structure_hits = sum(1 for h in self.REQUIRED_HINTS if h in text)
        breakdown["structure"] = structure_hits / len(self.REQUIRED_HINTS)

        # typing hint
        breakdown["typing"] = 1.0 if "->" in output or "typing" in text else 0.5

        # completeness heuristic (still heuristic, but explicit rubric)
        length = len(output)
        if length > 1500:
            breakdown["completeness"] = 1.0
        elif length > 800:
            breakdown["completeness"] = 0.7
        else:
            breakdown["completeness"] = 0.3

        score = sum(breakdown.values()) / len(breakdown)

        return ScoreResult(score, breakdown, "PLAN rubric score")


# =========================================================
# DISPATCHER
# =========================================================

def score_task(task: Dict[str, Any], output: str) -> ScoreResult:
    engine = ScoringEngine()
    return engine.score(task, output)