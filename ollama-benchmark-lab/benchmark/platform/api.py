from benchmark.analytics.engine import BenchmarkAnalytics
from benchmark.experiments.tracker import ExperimentTracker
from benchmark.leaderboard.engine import Leaderboard
from benchmark.registry.run_registry import RunRegistry
from benchmark.sandbox.docker_runner import DockerRunner
from benchmark.sandbox.docker_runner_v2 import DockerRunnerV2


class BenchmarkPlatform:
    """
    Central orchestration layer for SWE-bench research system.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}

        self.analytics = BenchmarkAnalytics()
        self.tracker = ExperimentTracker()
        self.leaderboard = Leaderboard()
        self.registry = RunRegistry()

    def run_experiment(self, config: dict, tasks: list[dict]):
        run_id = self.tracker.start_run(config)

        docker = DockerRunnerV2()
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

        score = (
            sum(r["passed"] for r in results) / len(results)
            if results else 0.0
        )

        self.leaderboard.record(config.get("model"), score)

        return {
            "run_id": run_id,
            "score": score,
            "tasks": len(results)
        }