"""
Unit tests for the leaderboard ranking logic.
"""

import pytest
from benchmark.leaderboard.engine import Leaderboard

def test_leaderboard_recording():
    """Test recording scores for different models."""
    lb = Leaderboard()
    lb.record("model-a", 0.8)
    lb.record("model-a", 0.9)
    lb.record("model-b", 0.5)

    assert len(lb.scores["model-a"]) == 2
    assert len(lb.scores["model-b"]) == 1

def test_leaderboard_ranking():
    """Test the mean-based ranking logic."""
    lb = Leaderboard()
    lb.record("model-a", 1.0)
    lb.record("model-a", 0.0)  # mean = 0.5
    lb.record("model-b", 0.8)  # mean = 0.8
    lb.record("model-c", 0.9)  # mean = 0.9

    ranking = lb.rank()
    
    # Expected order: model-c (0.9), model-b (0.8), model-a (0.5)
    assert ranking[0] == ("model-c", 0.9)
    assert ranking[1] == ("model-b", 0.8)
    assert ranking[2] == ("model-a", 0.5)

def test_empty_leaderboard():
    """Test ranking with no data."""
    lb = Leaderboard()
    assert lb.rank() == []
