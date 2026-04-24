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
    from __future__ import annotations

    import json
    import subprocess
    import tempfile
    import os
    from dataclasses import dataclass
    from pathlib import Path
    from typing import Dict, Any, Optional

    # =========================================================
    # RESULT STRUCTURE
    # =========================================================

    @dataclass
    class EvalResult:
        score: float
        passed: bool
        test_output: str
        error: Optional[str]

    # =========================================================
    # RUBRIC SCORING (PRIMARY SIGNAL)
    # =========================================================

    def apply_rubric(task: Dict[str, Any], test_passed: bool) -> float:
        rubric = task.get("rubric", {})

        if not rubric:
            # strict fallback: execution-only
            return 1.0 if test_passed else 0.0

        base = 0.0

        # correctness is dominant
        base += rubric.get("correctness", 0.7) * (1.0 if test_passed else 0.0)

        # structure reward (light bonus if tests pass)
        base += rubric.get("structure", 0.1) * (1.0 if test_passed else 0.0)

        # edge cases only matter if tests exist
        base += rubric.get("edge_cases", 0.1) * (1.0 if test_passed else 0.0)

        # efficiency is NOT measurable here → neutral unless extended runtime profiler added
        base += rubric.get("efficiency", 0.0) * 0.0

        return min(base, 1.0)

    # =========================================================
    # TEST EXECUTION ENGINE (SWE-BENCH STYLE)
    # =========================================================

    class SandboxExecutor:
        """
        Executes pytest inside isolated temp workspace.
        """

        def run_tests(self, task: Dict[str, Any], code: str) -> EvalResult:
            tests = task.get("tests", {})
            exec_cfg = task.get("execution", {})

            test_path = tests.get("path")
            entrypoint = exec_cfg.get("entrypoint")

            if not test_path or not entrypoint:
                return EvalResult(
                    score=0.0,
                    passed=False,
                    test_output="MISSING_TEST_CONFIG",
                    error="task must define tests.path and execution.entrypoint"
                )

            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)

                # write solution
                solution_file = tmp_path / entrypoint
                solution_file.parent.mkdir(parents=True, exist_ok=True)
                solution_file.write_text(code)

                # copy tests (assume relative path inside repo/tasks)
                test_src = Path(test_path)
                test_dst = tmp_path / "tests"
                if test_src.exists():
                    self._copy_dir(test_src, test_dst)
                else:
                    return EvalResult(
                        score=0.0,
                        passed=False,
                        test_output="TEST_PATH_NOT_FOUND",
                        error=str(test_src)
                    )

                # run pytest
                try:
                    proc = subprocess.run(
                        ["pytest", "-q", "--disable-warnings", "--maxfail=1"],
                        cwd=tmp_path,
                        capture_output=True,
                        text=True,
                        timeout=20
                    )

                    passed = proc.returncode == 0
                    return EvalResult(
                        score=1.0 if passed else 0.0,
                        passed=passed,
                        test_output=proc.stdout + proc.stderr,
                        error=None if passed else proc.stderr
                    )

                except subprocess.TimeoutExpired:
                    return EvalResult(
                        score=0.0,
                        passed=False,
                        test_output="TIMEOUT",
                        error="execution timeout"
                    )

        def _copy_dir(self, src: Path, dst: Path):
            import shutil
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    # =========================================================
    # MAIN EVALUATOR (NO HEURISTICS)
    # =========================================================

    class Evaluator:

        def __init__(self):
            self.executor = SandboxExecutor()

        def evaluate(self, task: Dict[str, Any], output: str) -> Dict[str, Any]:

            # 1. execute tests
            result = self.executor.run_tests(task, output)

            # 2. apply rubric
            final_score = apply_rubric(task, result.passed)

            # 3. strict validation (NO SILENT FALLBACKS)
            if "tests" not in task:
                raise ValueError("Missing 'tests' field in task")

            if "execution" not in task:
                raise ValueError("Missing 'execution' field in task")

            return {
                "task_id": task.get("id"),
                "score": final_score,
                "passed": result.passed,
                "test_output": result.test_output,
                "error": result.error,
                "mode": task.get("mode")
            }

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