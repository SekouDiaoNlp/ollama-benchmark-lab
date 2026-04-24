"""
Central analytics engine for SWE-bench results.

This module aggregates normalization, regression tracking, model comparison,
and failure clustering into a single high-level interface.

Example:
    >>> analytics = BenchmarkAnalytics()
    >>> normalized = analytics.process_run("model_v1", "task1", result_dict)
"""

from typing import Any, Dict, List

from benchmark.analytics.normalizer import ResultNormalizer
from benchmark.analytics.regression_tracker import RegressionTracker
from benchmark.analytics.model_compare import ModelComparator
from benchmark.analytics.failure_clustering import FailureClusterer


class BenchmarkAnalytics:
    """
    Central analytics engine for SWE-bench results.

    Attributes:
        normalizer (ResultNormalizer): Component for normalizing raw outputs.
        regression (RegressionTracker): Component for tracking execution history.
        comparator (ModelComparator): Component for scoring differentials between models.
        clusterer (FailureClusterer): Component for grouping test failures.
    """

    def __init__(self) -> None:
        """Initialize all analytical sub-components."""
        self.normalizer: ResultNormalizer = ResultNormalizer()
        self.regression: RegressionTracker = RegressionTracker()
        self.comparator: ModelComparator = ModelComparator()
        self.clusterer: FailureClusterer = FailureClusterer()

    def process_run(self, model_name: str, task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a raw result and record it in the regression history.

        Args:
            model_name (str): The identifier of the evaluated model.
            task_id (str): The identifier of the benchmark task.
            result (Dict[str, Any]): The raw execution output.

        Returns:
            Dict[str, Any]: The normalized evaluation payload.
        """
        normalized: Dict[str, Any] = self.normalizer.normalize(task_id, result)
        self.regression.record(model_name, normalized)
        return normalized

    def analyze_model(self, model_name: str) -> Dict[str, Any]:
        """
        Detect any performance regressions for a given model over its history.

        Args:
            model_name (str): The target model identifier.

        Returns:
            Dict[str, Any]: A dictionary containing a list of detected regressions.
        """
        regressions: List[Dict[str, Any]] = self.regression.detect_regressions(model_name)
        return {"regressions": regressions}

    def compare_models(self, a: List[Dict[str, Any]], b: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Compute the performance differential between two execution batches.

        Args:
            a (List[Dict[str, Any]]): Baseline model results.
            b (List[Dict[str, Any]]): Candidate model results.

        Returns:
            Dict[str, float]: Comparative metrics including the win/loss delta.
        """
        return self.comparator.compare(a, b)

    def failure_analysis(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Group failing test runs by their terminal error patterns.

        Args:
            results (List[Dict[str, Any]]): A list of normalized execution results.

        Returns:
            Dict[str, int]: A mapping of error signatures to their occurrence count.
        """
        return self.clusterer.cluster(results)