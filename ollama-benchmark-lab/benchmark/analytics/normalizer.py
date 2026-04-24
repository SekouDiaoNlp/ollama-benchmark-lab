"""
Data normalization pipeline for raw benchmark logs.

This module provides the ResultNormalizer class which converts highly nested
raw execution dictionaries into a flat, predictable schema for analytical use.

Example:
    >>> normalizer = ResultNormalizer()
    >>> clean = normalizer.normalize("task1", {"score": {"passed": True}})
"""

from typing import Any, Dict


class ResultNormalizer:
    """
    Converts raw execution results into a stable benchmark schema.
    """

    def normalize(self, task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten and standardize a raw benchmark execution payload.

        Args:
            task_id (str): The target task identifier.
            result (Dict[str, Any]): The raw, nested result from the execution engine.

        Returns:
            Dict[str, Any]: A flattened dictionary containing core metrics (passed, stdout, etc).
        """
        score_data = result.get("score")
        passed = False
        
        if isinstance(score_data, dict):
            passed = bool(score_data.get("passed", False))
        elif isinstance(score_data, (int, float)):
            passed = score_data > 0
            
        baseline_block: Dict[str, Any] = result.get("baseline", {})
        baseline_result: Dict[str, Any] = baseline_block.get("result", {})

        return {
            "task_id": task_id,
            "passed": passed,
            "exit_code": baseline_result.get("exit_code"),
            "stdout": str(baseline_result.get("stdout", "")),
            "stderr": str(baseline_result.get("stderr", "")),
            "timestamp": result.get("timestamp"),
        }