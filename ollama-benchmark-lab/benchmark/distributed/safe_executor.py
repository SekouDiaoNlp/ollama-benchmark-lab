"""
Safe execution strategy dispatcher.

This module provides the SafeExecutor class which selects the appropriate
execution backend (local replay or multiprocessing pool) for benchmark tasks.
"""

from typing import List, Dict, Any
from benchmark.distributed.worker_pool import WorkerPool
from benchmark.runtime.replay_engine import ReplayEngine

class SafeExecutor:
    """
    Coordinates execution of tasks using available local resources.

    Attributes:
        pool (WorkerPool): Multiprocessing worker pool.
        replay (ReplayEngine): Local task execution engine.
    """

    def __init__(self, workers: int = 4) -> None:
        """
        Initialize the executor with a specified worker count.

        Args:
            workers (int): Number of parallel worker processes.
        """
        self.pool: WorkerPool = WorkerPool(workers)
        self.replay: ReplayEngine = ReplayEngine()

    def run_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute a batch of tasks sequentially using the local replay engine.

        Note: Multi-task parallelization via the pool is initialized but not 
        yet wired for synchronous batch returns in this version.

        Args:
            tasks (List[Dict[str, Any]]): List of task configurations.

        Returns:
            List[Dict[str, Any]]: List of execution results.
        """
        results: List[Dict[str, Any]] = []

        for t in tasks:
            # ReplayEngine uses .run() as per current implementation
            results.append(self.replay.run(t))

        return results