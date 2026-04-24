"""
Model performance delta computation.

This module provides the ModelComparator class to calculate win/loss rates
and absolute performance deltas between two benchmark runs.

Example:
    >>> comp = ModelComparator()
    >>> comp.compare([{"passed": True}], [{"passed": False}])
    {'model_a_score': 1.0, 'model_b_score': 0.0, 'delta': -1.0}
"""

from typing import Any, Dict, List


class ModelComparator:
    """
    Compares performance across models.
    """

    def compare(
        self,
        model_a_results: List[Dict[str, Any]],
        model_b_results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate score percentages and performance delta between two models.

        Args:
            model_a_results (List[Dict[str, Any]]): Baseline evaluation outcomes.
            model_b_results (List[Dict[str, Any]]): Candidate evaluation outcomes.

        Returns:
            Dict[str, float]: A dictionary containing absolute scores and the relative delta.
        """
        a_pass: int = sum(1 for r in model_a_results if r.get("passed"))
        b_pass: int = sum(1 for r in model_b_results if r.get("passed"))

        total: int = len(model_a_results)

        return {
            "model_a_score": a_pass / total if total else 0.0,
            "model_b_score": b_pass / total if total else 0.0,
            "delta": (b_pass - a_pass) / total if total else 0.0
        }