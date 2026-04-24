"""
Unit tests for the evaluation logic in benchmark/evaluator.py.
"""

import pytest
from benchmark.evaluator import normalize_text, is_valid_python, RealEvaluator

def test_normalize_text():
    """Test text normalization across various input formats."""
    assert normalize_text("  Hello   World  ") == "hello world"
    assert normalize_text("UPPER CASE") == "upper case"
    assert normalize_text(None) == ""
    assert normalize_text("\nLine\nBreak\tTab") == "line break tab"

@pytest.mark.parametrize("code, expected", [
    ("def foo(): pass", True),
    ("invalid code {", False),
    ("x = 1 + 2", True),
    ("", True),  # Empty string is technically valid AST (Module with no body)
])
def test_is_valid_python(code, expected):
    """Test Python syntax validation."""
    assert is_valid_python(code) == expected

class TestRealEvaluator:
    """Test suite for the RealEvaluator scoring logic."""

    def test_score_act_exact_match(self):
        evaluator = RealEvaluator()
        task = {"mode": "ACT", "expected": "42"}
        # exact match (0.7) + containment (0.3) = 1.0
        assert evaluator.score(task, "42") == 1.0

    def test_score_act_containment(self):
        evaluator = RealEvaluator()
        task = {"mode": "ACT", "expected": "42"}
        # containment only (0.3)
        score = evaluator.score(task, "The answer is 42.")
        assert score == pytest.approx(0.3)

    def test_score_act_no_match(self):
        evaluator = RealEvaluator()
        task = {"mode": "ACT", "expected": "42"}
        assert evaluator.score(task, "something else") == 0.0

    def test_score_plan_structural(self):
        evaluator = RealEvaluator()
        task = {"mode": "PLAN"}
        # Basic scoring for non-empty output
        score = evaluator.score(task, "def architecture(): return True")
        assert score > 0.0
        assert score <= 1.0

    def test_fallback_mode(self):
        evaluator = RealEvaluator()
        task = {"mode": "UNKNOWN"}
        assert evaluator.score(task, "some output") == 1.0
        assert evaluator.score(task, "") == 0.0
