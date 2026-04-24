"""
Unit tests for the analytics engine.
"""

import pytest
from benchmark.analytics.engine import BenchmarkAnalytics

def test_analytics_process_run():
    """Test result processing in the analytics engine."""
    analytics = BenchmarkAnalytics()
    result = {"status": "pass", "score": 1.0}
    
    normalized = analytics.process_run("m1", "t1", result)
    
    assert normalized is not None
    # Assuming ResultNormalizer adds some keys or just returns normalized dict
    assert isinstance(normalized, dict)

def test_analytics_compare():
    """Test model comparison."""
    analytics = BenchmarkAnalytics()
    a = [{"task_id": "t1", "score": 0.5}]
    b = [{"task_id": "t1", "score": 1.0}]
    
def test_analytics_analyze_model():
    """Test model analysis for regressions."""
    analytics = BenchmarkAnalytics()
    analytics.process_run("m1", "t1", {"score": 1.0})
    analytics.process_run("m1", "t1", {"score": 0.0}) # Regression
    
    analysis = analytics.analyze_model("m1")
    assert len(analysis["regressions"]) == 1

def test_analytics_failure_analysis():
    """Test clustering of failures."""
    analytics = BenchmarkAnalytics()
    results = [
        {"task_id": "t1", "passed": False, "stderr": "Err1"},
        {"task_id": "t2", "passed": False, "stderr": "Err1"}
    ]
    
    analysis = analytics.failure_analysis(results)
    assert analysis["Err1"] == 2
