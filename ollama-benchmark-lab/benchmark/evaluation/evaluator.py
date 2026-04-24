"""
Validation and evaluation layer for benchmark datasets.

This module provides the Evaluator class to validate benchmark task payload
contracts and to compute final execution scores.

Example:
    >>> evaluator = Evaluator(strict=True)
    >>> res = evaluator.evaluate({"version": "v3", "tests": {"path": "/"}}, {"success": True})
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# =========================================================
# COMPATIBILITY LAYER
# =========================================================

def get_tests_path(task: Dict[str, Any]) -> Optional[str]:
    """
    Extract the tests path from the task configuration.

    Supports the v3 dictionary format: {"tests": {"path": "..."}}.
    Legacy string formats are rejected in strict validation.

    Args:
        task (Dict[str, Any]): The benchmark task dictionary.

    Returns:
        Optional[str]: The extracted path or None if not found or invalid.
    """
    tests: Any = task.get("tests", {})

    if isinstance(tests, str):
        # legacy format not supported in strict mode
        return None

    if isinstance(tests, dict):
        result: Optional[str] = tests.get("path")
        return result

    return None


def get_entrypoint(task: Dict[str, Any]) -> Optional[str]:
    """
    Extract the execution command for the sandbox runner.

    Args:
        task (Dict[str, Any]): The benchmark task dictionary.

    Returns:
        Optional[str]: The execution entrypoint command or None if missing.
    """
    exec_block: Any = task.get("execution", {})

    if not isinstance(exec_block, dict):
        return None

    result: Optional[str] = exec_block.get("entrypoint")
    return result


# =========================================================
# VALIDATION CORE
# =========================================================

class Evaluator:
    """
    Validates task schemas and computes scores based on benchmark results.

    Attributes:
        strict (bool): Whether to enforce strict task schema validation.
    """

    def __init__(self, strict: bool = True) -> None:
        """
        Initialize the evaluator.

        Args:
            strict (bool): Enable strict schema enforcement.
        """
        self.strict: bool = strict

    # -----------------------------------------------------
    # MAIN ENTRY
    # -----------------------------------------------------

    def evaluate(self, task: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate task requirements and compute the final score.

        Args:
            task (Dict[str, Any]): The configuration of the executed task.
            result (Dict[str, Any]): The output from the benchmark runner.

        Returns:
            Dict[str, Any]: A dictionary containing status, errors, warnings, and the score.
        """
        errors: List[str] = []
        warnings: List[str] = []

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

        tests_path: Optional[str] = get_tests_path(task)
        entrypoint: Optional[str] = get_entrypoint(task)

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

        score: float = self._compute_score(task, result)

        return {
            "status": "ok",
            "errors": errors,
            "warnings": warnings,
            "score": score
        }

    # -----------------------------------------------------
    # SCORING LOGIC
    # -----------------------------------------------------

    def _compute_score(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        """
        Compute a safe default score based on execution success.

        Args:
            task (Dict[str, Any]): The task context.
            result (Dict[str, Any]): The execution payload.

        Returns:
            float: 1.0 if successful, 0.0 otherwise.
        """
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

    sample_task: Dict[str, Any] = {
        "id": "demo",
        "public_prompt": "test",
        "version": "v3",
        "tests": {"path": "tests/"},
        "execution": {"entrypoint": "pytest -q"}
    }

    sample_result: Dict[str, Any] = {"success": True}

    ev = Evaluator(strict=True)
    print(ev.evaluate(sample_task, sample_result))