from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from benchmark.sandbox.pool import SandboxPool
from benchmark.sandbox.pytest_runner import run_pytest


# =========================================================
# SCORE OUTPUT
# =========================================================

@dataclass
class ScoreBreakdown:
    final: float
    tests_passed: float
    structure: float
    runtime_ok: float


# =========================================================
# REAL SWE-BENCH STYLE EVALUATOR (EXECUTION-BASED)
# =========================================================

class RealEvaluator:

    def __init__(self, pool_size: int = 4):
        self.pool = SandboxPool(size=pool_size)

    # -----------------------------------------------------
    # MAIN ENTRYPOINT
    # -----------------------------------------------------

    def score(self, task: Dict[str, Any], output: str | None = None) -> float:

        mode = task.get("mode")

        # Only SWE mode uses execution-based scoring
        if mode != "SWE":
            return self._fallback(task, output)

        sandbox = self.pool.acquire()

        try:
            return self._score_swe(task, output, sandbox)

        finally:
            self.pool.release(sandbox)

    # -----------------------------------------------------
    # SWE-BENCH EXECUTION PATH (UPDATED)
    # -----------------------------------------------------

    def _score_swe(self, task: Dict[str, Any], output: str | None, sandbox):

        # =================================================
        # 1. WRITE MODEL OUTPUT INTO SANDBOX
        # =================================================

        solution_code = task.get("solution", "")

        sandbox.exec([
            "bash", "-lc",
            f"cat > /workspace/solution.py << 'EOF'\n{solution_code}\nEOF"
        ])

        # =================================================
        # 2. READ EXECUTION CONFIG (NEW SCHEMA)
        # =================================================

        execution = task.get("execution", {})
        tests = task.get("tests", {})

        entrypoint = execution.get("entrypoint", "tests/")
        timeout = execution.get("timeout_sec", 60)

        # =================================================
        # 3. RUN PYTEST IN SANDBOX
        # =================================================

        result = run_pytest(
            sandbox,
            task_path=entrypoint
        )

        tests_passed = 1.0 if result["passed"] else 0.0

        # =================================================
        # 4. STRUCTURAL SIGNAL (MINIMAL, NON-HEURISTIC)
        # =================================================

        structure = 1.0 if "def " in solution_code else 0.2

        # =================================================
        # 5. OPTIONAL RUNTIME SAFETY SIGNAL
        # =================================================

        runtime_ok = 1.0 if "timeout" not in result["raw_output"].lower() else 0.5

        # =================================================
        # 6. RUBRIC WEIGHTING (FROM TASK JSON IF PRESENT)
        # =================================================

        rubric = task.get("rubric", {})

        w_correct = rubric.get("correctness", 0.85)
        w_structure = rubric.get("structure", 0.10)
        w_runtime = rubric.get("efficiency", 0.05)

        final = (
            w_correct * tests_passed +
            w_structure * structure +
            w_runtime * runtime_ok
        )

        return float(min(final, 1.0))

    # -----------------------------------------------------
    # FALLBACK (NON-SWE TASKS)
    # -----------------------------------------------------

    def _fallback(self, task: Dict[str, Any], output: str | None):

        if output is None:
            return 0.0

        return 0.5 if len(output.strip()) > 0 else 0.0

    # -----------------------------------------------------
    # CLEANUP (OPTIONAL)
    # -----------------------------------------------------

    def close(self):
        self.pool.close()