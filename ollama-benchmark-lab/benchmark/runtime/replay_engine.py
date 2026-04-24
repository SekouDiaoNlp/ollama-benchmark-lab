"""
Deterministic task execution and replay engine.

This module provides the ReplayEngine class, which orchestrates the caching
and re-execution of research tasks to avoid redundant processing.

Example:
    >>> engine = ReplayEngine()
    >>> res = engine.run({"id": "task1", "command": "echo test"})
"""

from typing import Any, Dict

from benchmark.cache.execution_cache import ExecutionCache
from benchmark.runtime.research_executor import run_research_task

# Global cache instance for persistent execution tracking
cache = ExecutionCache()


class ReplayEngine:
    """
    Replays SWE-bench runs deterministically, utilizing a cache mechanism.
    """

    def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task or load its result from the cache if previously completed.

        Args:
            task (Dict[str, Any]): The configuration dictionary for the research task.

        Returns:
            Dict[str, Any]: The execution result payload.
        """
        if cache.exists(task):
            cached_result: Dict[str, Any] = cache.load(task)
            return cached_result

        result: Dict[str, Any] = run_research_task(task)
        cache.save(task, result)

        return result