from benchmark.distributed.worker_pool import WorkerPool
from benchmark.runtime.replay_engine import ReplayEngine


class SafeExecutor:
    """
    Chooses execution strategy safely:
    - local replay
    - multiprocessing
    - Ray (optional future hook)
    """

    def __init__(self, workers=4):
        self.pool = WorkerPool(workers)
        self.replay = ReplayEngine()

    def run_tasks(self, tasks: list[dict]):
        results = []

        for t in tasks:
            results.append(self.replay.run(t))

        return results