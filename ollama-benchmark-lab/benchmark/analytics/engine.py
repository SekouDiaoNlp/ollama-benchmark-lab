from benchmark.analytics.normalizer import ResultNormalizer
from benchmark.analytics.regression_tracker import RegressionTracker
from benchmark.analytics.model_compare import ModelComparator
from benchmark.analytics.failure_clustering import FailureClusterer


class BenchmarkAnalytics:
    """
    Central analytics engine for SWE-bench results.
    """

    def __init__(self):
        self.normalizer = ResultNormalizer()
        self.regression = RegressionTracker()
        self.comparator = ModelComparator()
        self.clusterer = FailureClusterer()

    def process_run(self, model_name: str, task_id: str, result: dict):
        normalized = self.normalizer.normalize(task_id, result)
        self.regression.record(model_name, normalized)
        return normalized

    def analyze_model(self, model_name: str):
        regressions = self.regression.detect_regressions(model_name)
        return {"regressions": regressions}

    def compare_models(self, a, b):
        return self.comparator.compare(a, b)

    def failure_analysis(self, results):
        return self.clusterer.cluster(results)