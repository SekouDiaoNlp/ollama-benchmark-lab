from __future__ import annotations

from typing import Dict, Any, List


def load_golden_tasks() -> List[Dict[str, Any]]:
    """
    Deterministic regression test suite.
    Used to detect evaluator drift.
    """

    return [
        {
            "id": "golden_addition",
            "mode": "ACT",
            "public_prompt": "Return the sum of 2 + 2 as a string.",
            "expected": "4",
            "rubric": {"correctness": 1.0}
        },
        {
            "id": "golden_palindrome",
            "mode": "ACT",
            "public_prompt": "Return True if 'racecar' is a palindrome.",
            "expected": "True",
            "rubric": {"correctness": 1.0}
        },
        {
            "id": "golden_sort",
            "mode": "SWE",
            "public_prompt": "Implement Python sort function.",
            "tests": "def test_sort(): assert sorted([3,1,2]) == [1,2,3]",
            "rubric": {"correctness": 1.0}
        }
    ]