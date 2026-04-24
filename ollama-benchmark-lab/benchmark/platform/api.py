from benchmark.analytics.engine import BenchmarkAnalytics
from benchmark.experiments.tracker import ExperimentTracker
from benchmark.leaderboard.engine import Leaderboard
from benchmark.registry.run_registry import RunRegistry


class BenchmarkPlatform:
    """
    Central orchestration layer for SWE-bench research system.
    """

    def __init__(self):
        self.analytics = BenchmarkAnalytics()
        self.tracker = ExperimentTracker()
        self.leaderboard = Leaderboard()
        self.registry = RunRegistry()

    def run_experiment(self, config: dict, results: list[dict]):
        run_id = self.tracker.start_run(config)

        for r in results:
            self.tracker.log_result(run_id, r)

            model = config.get("model", "unknown")
            self.analytics.process_run(model, r["task_id"], r)

        final = self.tracker.end_run(run_id)

        self.registry.add(final)

        score = sum(
            r.get("passed", 0) for r in results
        ) / len(results)

        self.leaderboard.record(config.get("model", "unknown"), score)

        return {
            "run_id": run_id,
            "score": score
        }