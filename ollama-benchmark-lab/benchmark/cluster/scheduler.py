"""
Distributed task scheduler using Ray.

This module provides the Scheduler class which manages the submission
and collection of remote tasks in a Ray cluster.
"""

import ray
from typing import Any, Dict, List
from benchmark.cluster.ray_worker import run_task

class Scheduler:
    """
    Manages distributed execution of benchmark tasks.
    """

    def run(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Submit tasks to the Ray cluster and wait for completion.

        Args:
            tasks (List[Dict[str, Any]]): A list of benchmark task configurations.

        Returns:
            List[Dict[str, Any]]: A list of execution results in the same order as input.
        """
        futures = [run_task.remote(t) for t in tasks]
        results: List[Dict[str, Any]] = ray.get(futures)
        return results