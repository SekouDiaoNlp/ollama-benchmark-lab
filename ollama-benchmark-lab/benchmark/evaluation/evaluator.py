from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple, List


# =========================================================
# COMPATIBILITY LAYER (CRITICAL FIX)
# =========================================================

def get_tests_path(task: Dict[str, Any]):
    """
    Supports:
    - v3: {"tests": {"path": "..."}}
    - legacy: {"tests": "..."} (string)
    """
    tests = task.get("tests", {})

    if isinstance(tests, str):
        # legacy format not supported in strict mode
        return None

    if isinstance(tests, dict):
        return tests.get("path")

    return None


def get_entrypoint(task: Dict[str, Any]):
    """
    Execution command for sandbox runner.
    """
    exec_block = task.get("execution", {})

    if not isinstance(exec_block, dict):
        return None

    return exec_block.get("entrypoint")


# =========================================================
# VALIDATION CORE
# =========================================================

class Evaluator:

    def __init__(self, strict: bool = True):
        self.strict = strict

    # -----------------------------------------------------
    # MAIN ENTRY
    # -----------------------------------------------------

    def evaluate(self, task: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:

        errors = []
        warnings = []

        # -----------------------------
        # REQUIRED FIELD VALIDATION
        # -----------------------------

        if not task.get("public_prompt"):
            errors.append("missing_field:public_prompt")

        if not task.get("version"):
            errors.append("missing_field:version")

        # -----------------------------
        # SWE-BENCH EXECUTION CONTRACT
        # -----------------------------

        tests_path = get_tests_path(task)
        entrypoint = get_entrypoint(task)

        if not tests_path:
            errors.append("tests.path missing")

        if not entrypoint:
            errors.append("execution.entrypoint missing")

        # -----------------------------
        # STRICT MODE BEHAVIOR
        # -----------------------------

        if self.strict and errors:
            return {
                "status": "invalid_task",
                "errors": errors,
                "warnings": warnings,
                "score": 0.0
            }

        # -----------------------------
        # SCORE COMPUTATION (SAFE DEFAULT)
        # -----------------------------

        score = self._compute_score(task, result)

        return {
            "status": "ok",
            "errors": errors,
            "warnings": warnings,
            "score": score
        }

    # -----------------------------------------------------
    # SCORING LOGIC (PLACEHOLDER SAFE DEFAULT)
    # -----------------------------------------------------

    def _compute_score(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:

        # if execution failed entirely
        if not result:
            return 0.0

        if result.get("success") is True:
            return 1.0

        return 0.0


# =========================================================
# OPTIONAL CLI TEST ENTRY
# =========================================================

if __name__ == "__main__":

    sample_task = {
        "id": "demo",
        "public_prompt": "test",
        "version": "v3",
        "tests": {"path": "tests/"},
        "execution": {"entrypoint": "pytest -q"}
    }

    sample_result = {"success": True}

    ev = Evaluator(strict=True)
    print(ev.evaluate(sample_task, sample_result))