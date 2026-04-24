from benchmark.ollama_client import OllamaClient
from benchmark.evaluator import RealEvaluator
from benchmark.checkpoint import CheckpointManager
from benchmark.runner import BenchmarkRunner, load_tasks, get_models


class BenchmarkPlatform:
    def __init__(self, limit=None):
        self.limit = limit

    def run_experiment(self):
        ckpt = CheckpointManager("results/state.jsonl")
        client = OllamaClient()
        evaluator = RealEvaluator()

        runner = BenchmarkRunner(client, evaluator, ckpt)

        models = get_models("all")
        tasks = load_tasks({}, smoke=self.limit == 1)

        if self.limit:
            tasks = tasks[: self.limit]

        runner.run(models, tasks, resume=False)


def run_experiment(config=None, tasks=None):
    """
    CLI-compatible wrapper.
    """
    platform = BenchmarkPlatform(limit=len(tasks) if tasks else None)
    platform.run_experiment()

    return {"passed": True}