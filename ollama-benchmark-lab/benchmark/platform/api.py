from benchmark.analytics.engine import BenchmarkAnalytics
from benchmark.experiments.tracker import ExperimentTracker
from benchmark.leaderboard.engine import Leaderboard
from benchmark.registry.run_registry import RunRegistry
from benchmark.sandbox.docker_runner import DockerRunner


class BenchmarkPlatform:
    """
    Central orchestration layer for SWE-bench research system.
    """

    def __init__(self):
        self.analytics = BenchmarkAnalytics()
        self.tracker = ExperimentTracker()
        self.leaderboard = Leaderboard()
        self.registry = RunRegistry()

    def run_experiment(self, config: dict, tasks: list[dict]):
        run_id = self.tracker.start_run(config)

        docker = DockerRunner()
        results = []

        for task in tasks:
            result = docker.run(task)

            results.append(result)

            model = config.get("model", "unknown")
            self.analytics.process_run(
                model,
                result["task_id"],
                result
            )

            self.tracker.log_result(run_id, result)

        self.tracker.end_run(run_id)

        score = sum(r["passed"] for r in results) / len(results)

        self.leaderboard.record(config.get("model"), score)

        return {
            "run_id": run_id,
            "score": score,
            "tasks": len(results)
        }