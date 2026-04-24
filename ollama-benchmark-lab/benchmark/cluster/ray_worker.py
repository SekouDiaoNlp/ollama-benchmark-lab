"""
Distributed worker implementation using Ray.

This module provides a remote Ray task for executing benchmark tasks
in parallel across a cluster.
"""

import ray
from typing import Any, Dict
from benchmark.replay.engine import ReplayEngine

# Ensure Ray is initialized for the worker process
ray.init(ignore_reinit_error=True)

# Global engine instance for reuse across tasks on the same worker
engine: ReplayEngine = ReplayEngine()

@ray.remote
def run_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single benchmark task remotely.

    Args:
        task (Dict[str, Any]): The benchmark task configuration.

    Returns:
        Dict[str, Any]: The execution result.
    """
    return engine.run(task)