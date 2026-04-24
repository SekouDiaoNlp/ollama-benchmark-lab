from _typeshed import Incomplete
from benchmark.distributed.worker_pool import WorkerPool as WorkerPool
from benchmark.runtime.replay_engine import ReplayEngine as ReplayEngine

class SafeExecutor:
    pool: Incomplete
    replay: Incomplete
    def __init__(self, workers: int = 4) -> None: ...
    def run_tasks(self, tasks: list[dict]): ...
