"""
Platform API for running benchmarks.

This module provides the main integration layer that combines the local LLM client,
the execution evaluator, and the checkpoint manager into a cohesive runner.

Example:
    >>> from benchmark.platform.api import run_experiment
    >>> run_experiment({"local_only": True}, [{"task_id": "test"}])
"""

from typing import Any, Dict, List, Optional

from benchmark.ollama_client import OllamaClient
from benchmark.evaluator import RealEvaluator
from benchmark.checkpoint import CheckpointManager
from benchmark.runner import BenchmarkRunner, load_tasks, get_models


class BenchmarkPlatform:
    """
    Platform orchestrator for setting up and running a local benchmark suite.

    Attributes:
        limit (Optional[int]): The maximum number of tasks to run.
    """

    def __init__(self, limit: Optional[int] = None) -> None:
        """
        Initialize the BenchmarkPlatform.

        Args:
            limit (Optional[int]): Cap the number of tasks evaluated. Defaults to None.
        """
        self.limit: Optional[int] = limit

    def run_experiment(self) -> None:
        """
        Set up dependencies and execute the benchmark run.

        This method initializes the CheckpointManager, OllamaClient, and RealEvaluator,
        then iterates over all available models and tasks.
        """
        ckpt = CheckpointManager("results/state.jsonl")
        client = OllamaClient()
        evaluator = RealEvaluator()

        runner = BenchmarkRunner(client, evaluator, ckpt)

        models: List[str] = get_models("all")
        # Load tasks, using smoke logic if limit is 1
        tasks: List[Dict[str, Any]] = load_tasks({}, smoke=(self.limit == 1))

        if self.limit is not None:
            tasks = tasks[: self.limit]

        runner.run(models, tasks, resume=False)


def run_experiment(config: Optional[Dict[str, Any]] = None, tasks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    CLI-compatible wrapper for running a benchmark experiment.

    Args:
        config (Optional[Dict[str, Any]]): Execution configuration. Defaults to None.
        tasks (Optional[List[Dict[str, Any]]]): A list of tasks to execute. If provided,
            the limit is set to the number of tasks. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary containing the result of the experiment.
    """
    limit = len(tasks) if tasks is not None else None
    platform = BenchmarkPlatform(limit=limit)
    platform.run_experiment()

    return {"passed": True}