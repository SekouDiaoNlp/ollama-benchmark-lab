"""
Lightweight experiment tracking system.

This module provides the ExperimentTracker class for managing the lifecycle
of a benchmark run, including configuration storage and result logging.
"""

import time
import uuid
from typing import Any, Dict, List

class ExperimentTracker:
    """
    Tracks the progress and results of benchmark experiments.

    Attributes:
        runs (Dict[str, Dict[str, Any]]): In-memory store of experiments indexed by run ID.
    """

    def __init__(self) -> None:
        """
        Initialize the experiment tracker.
        """
        self.runs: Dict[str, Dict[str, Any]] = {}

    def start_run(self, config: Dict[str, Any]) -> str:
        """
        Initialize a new experiment run.

        Args:
            config (Dict[str, Any]): The configuration dictionary for this run.

        Returns:
            str: A unique identifier for the new run.
        """
        run_id: str = str(uuid.uuid4())

        self.runs[run_id] = {
            "config": config,
            "start_time": time.time(),
            "results": []
        }

        return run_id

    def log_result(self, run_id: str, result: Dict[str, Any]) -> None:
        """
        Append a task result to an active experiment run.

        Args:
            run_id (str): The ID of the target run.
            result (Dict[str, Any]): The task execution result to log.
        """
        if run_id in self.runs:
            self.runs[run_id]["results"].append(result)

    def end_run(self, run_id: str) -> Dict[str, Any]:
        """
        Mark an experiment run as complete and record the end time.

        Args:
            run_id (str): The ID of the run to end.

        Returns:
            Dict[str, Any]: The complete run data including configuration and results.

        Raises:
            KeyError: If the run_id is not found.
        """
        if run_id not in self.runs:
            raise KeyError(f"Run ID {run_id} not found")

        self.runs[run_id]["end_time"] = time.time()
        return self.runs[run_id]