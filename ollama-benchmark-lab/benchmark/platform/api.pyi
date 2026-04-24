from _typeshed import Incomplete
from benchmark.checkpoint import CheckpointManager as CheckpointManager
from benchmark.evaluator import RealEvaluator as RealEvaluator
from benchmark.ollama_client import OllamaClient as OllamaClient
from benchmark.runner import BenchmarkRunner as BenchmarkRunner, get_models as get_models, load_tasks as load_tasks

class BenchmarkPlatform:
    limit: Incomplete
    def __init__(self, limit=None) -> None: ...
    def run_experiment(self) -> None: ...

def run_experiment(config=None, tasks=None): ...
