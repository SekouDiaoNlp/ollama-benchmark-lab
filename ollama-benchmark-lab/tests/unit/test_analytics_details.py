"""
Unit tests for regression tracking and failure clustering.
"""

import pytest
from benchmark.analytics.regression_tracker import RegressionTracker
from benchmark.analytics.failure_clustering import FailureClusterer

def test_regression_tracker():
    """Test recording and detecting regressions."""
    tracker = RegressionTracker()
    
    # Baseline
    tracker.record("m1", {"task_id": "t1", "passed": True})
    
    # Improved/Same
    tracker.record("m1", {"task_id": "t1", "passed": True})
    assert len(tracker.detect_regressions("m1")) == 0
    
    # Regression
    tracker.record("m1", {"task_id": "t1", "passed": False})
    regressions = tracker.detect_regressions("m1")
    assert len(regressions) == 1
    assert regressions[0]["task_id"] == "t1"

def test_failure_clusterer():
    """Test grouping failures by stderr patterns."""
    clusterer = FailureClusterer()
    results = [
        {"task_id": "t1", "passed": False, "stderr": "ModuleNotFoundError: numpy"},
        {"task_id": "t2", "passed": False, "stderr": "ModuleNotFoundError: numpy"},
        {"task_id": "t3", "passed": False, "stderr": "SyntaxError: invalid syntax"},
        {"task_id": "t4", "passed": True, "stderr": ""}
    ]
    
    clusters = clusterer.cluster(results)
    
    # Should group t1 and t2 together
    assert clusters["ModuleNotFoundError: numpy"] == 2
    assert clusters["SyntaxError: invalid syntax"] == 1
    # Should not include passed tasks
    assert "" not in clusters
