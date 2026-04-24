"""
Property-based tests for text normalization invariants.
"""

from hypothesis import given, strategies as st
from benchmark.evaluator import normalize_text

@given(st.text())
def test_normalize_idempotence(t):
    """Applying normalization twice should yield the same result."""
    once = normalize_text(t)
    twice = normalize_text(once)
    assert once == twice

@given(st.text())
def test_normalize_lowercase(t):
    """Result should always be lowercase (if not empty)."""
    result = normalize_text(t)
    if result:
        assert result == result.lower()

@given(st.lists(st.text(min_size=1), min_size=1))
def test_normalize_whitespace_collapse(parts):
    """Multiple spaces/tabs/newlines should be collapsed into single spaces."""
    # Create a string with irregular whitespace between parts
    input_str = " \n\t ".join(parts)
    result = normalize_text(input_str)
    
    # Result should not contain double spaces
    assert "  " not in result
    # Result should not contain tabs or newlines
    assert "\t" not in result
    assert "\n" not in result
