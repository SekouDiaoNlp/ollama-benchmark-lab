"""
Multiprocessing worker pool for local task distribution.

This module provides a lightweight WorkerPool class that manages 
parallel execution of research tasks using standard Python multiprocessing.
"""

import multiprocessing as mp
from typing import List, Dict, Any, Optional
from benchmark.runtime.research_executor import run_research_task

class WorkerPool:
    """
    Manages a set of worker processes for parallel task execution.
    """

    def __init__(self, workers: int = 4) -> None:
        """
        Initialize the worker pool.

        Args:
            workers (int): Number of worker processes to spawn.
        """
        self.workers: int = workers
        # Use multiprocessing queue for cross-process communication
        self.queue: mp.Queue[Optional[Dict[str, Any]]] = mp.Queue()

    def _worker(self) -> None:
        """
        Internal worker loop that consumes tasks from the queue.
        """
        while True:
            task: Optional[Dict[str, Any]] = self.queue.get()
            if task is None:
                break
            run_research_task(task)

    def run(self, tasks: List[Dict[str, Any]]) -> None:
        """
        Distribute tasks across the worker pool and wait for completion.

        Args:
            tasks (List[Dict[str, Any]]): List of task configurations.
        """
        processes: List[mp.Process] = []

        for _ in range(self.workers):
            p = mp.Process(target=self._worker)
            p.start()
            processes.append(p)

        for t in tasks:
            self.queue.put(t)

        # Poison pill to stop workers
        for _ in processes:
            self.queue.put(None)

        for p in processes:
            p.join()