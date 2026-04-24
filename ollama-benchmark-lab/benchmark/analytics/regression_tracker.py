"""
Temporal performance tracking for benchmark targets.

This module provides the RegressionTracker class to store historical execution
results and flag any tasks that flip from 'passed' to 'failed' between runs.

Example:
    >>> tracker = RegressionTracker()
    >>> tracker.record("model1", {"task_id": "1", "passed": True})
    >>> tracker.record("model1", {"task_id": "1", "passed": False})
    >>> tracker.detect_regressions("model1")
"""

from collections import defaultdict
from typing import Any, Dict, List


class RegressionTracker:
    """
    Tracks performance changes across runs to identify regressions.

    Attributes:
        history (Dict[str, List[Dict[str, Any]]]): In-memory store of past runs mapped by model.
    """

    def __init__(self) -> None:
        """Initialize an empty run history database."""
        self.history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def record(self, model_name: str, result: Dict[str, Any]) -> None:
        """
        Log an execution result for a specific model.

        Args:
            model_name (str): The identifier for the tested model.
            result (Dict[str, Any]): The normalized benchmark result payload.
        """
        self.history[model_name].append(result)

    def detect_regressions(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Scan a model's run history for tasks that previously passed but now fail.

        Args:
            model_name (str): The target model identifier.

        Returns:
            List[Dict[str, Any]]: A list of detected regression payloads.
        """
        runs: List[Dict[str, Any]] = self.history[model_name]

        if len(runs) < 2:
            return []

        regressions: List[Dict[str, Any]] = []

        for prev, curr in zip(runs, runs[1:]):
            if prev.get("passed") and not curr.get("passed"):
                regressions.append({
                    "task_id": curr.get("task_id"),
                    "type": "performance_drop"
                })

        return regressions