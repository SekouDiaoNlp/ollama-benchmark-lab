"""
Scoring and aggregation logic for benchmark results.

This module provides utilities to score individual test results and
aggregate them into high-level pass rates for reporting.

Example:
    >>> res = [{"status": "passed"}, {"status": "failed"}]
    >>> aggregate(res)
    {'total': 2, 'passed': 1, 'pass_rate': 0.5}
"""

from typing import Any, Dict, List


def score_result(result: Dict[str, Any]) -> int:
    """
    Determine the binary score of a single execution result.

    Args:
        result (Dict[str, Any]): The execution result dictionary.

    Returns:
        int: 1 if the status is 'passed', otherwise 0.
    """
    return 1 if result.get("status") == "passed" else 0


def aggregate(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate multiple test results into a summary dictionary.

    Args:
        results (List[Dict[str, Any]]): A list of execution results.

    Returns:
        Dict[str, Any]: A dictionary containing total runs, passed runs, and the pass rate.
    """
    scores: List[int] = [score_result(r) for r in results]

    return {
        "total": len(results),
        "passed": sum(scores),
        "pass_rate": sum(scores) / len(results) if results else 0.0
    }