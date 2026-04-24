from _typeshed import Incomplete
from benchmark.checkpoint import CheckpointManager as CheckpointManager
from benchmark.evaluator import RealEvaluator as RealEvaluator
from benchmark.ollama_client import OllamaClient as OllamaClient
from dataclasses import dataclass
from typing import Any

ROOT: Incomplete
RESULTS_DIR: Incomplete
STATE_FILE: Incomplete

def get_models(mode: str) -> list[str]: ...
def load_tasks(cfg: dict[str, Any], smoke: bool = False) -> list[dict[str, Any]]: ...
def heartbeat(model: str, task_id: str): ...

@dataclass
class RunResult:
    model: str
    task_id: str
    score: float
    latency_s: float

class BenchmarkRunner:
    client: Incomplete
    evaluator: Incomplete
    ckpt: Incomplete
    def __init__(self, client: OllamaClient, evaluator: RealEvaluator, ckpt: CheckpointManager) -> None: ...
    def run_task(self, model: str, task: dict[str, Any]) -> RunResult: ...
    def run(self, models: list[str], tasks: list[dict[str, Any]], resume: bool): ...

def main() -> None: ...
