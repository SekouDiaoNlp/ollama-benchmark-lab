"""
Command Line Interface for Autollama.

This module provides the main entry point for running the local LLM benchmark tasks.
It integrates with the benchmark platform API to execute generated tasks.

Example:
    >>> from autollama.cli import main
    >>> # main() will parse arguments and execute the workflow
"""

import argparse
from typing import Any, Dict, List

from benchmark.platform.api import run_experiment
from benchmark.utils.console import Console

console = Console()


def load_tasks(limit: int = 1) -> List[Dict[str, Any]]:
    """
    Load a list of sample tasks for the benchmark.

    Args:
        limit (int): The maximum number of tasks to load. Defaults to 1.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the tasks.
    """
    return [
        {
            "task_id": "sample-001",
            "repo_url": "https://github.com/example/repo.git",
            "commit": "HEAD",
            "execution": {
                "entrypoint": "pytest -q"
            }
        }
    ][:limit]


def main() -> None:
    """
    Main entry point for the Autollama CLI.

    Parses command-line arguments and initiates the benchmarking process
    using the local LLM platform.

    Raises:
        Exception: If a task execution fails, the exception is caught and logged.
    """
    parser = argparse.ArgumentParser(description="Autollama Benchmarking CLI")
    parser.add_argument("--limit", type=int, default=1, help="Limit number of tasks")
    args = parser.parse_args()

    console.info("Autollama starting...")
    console.step("Loading tasks...")

    config: Dict[str, bool] = {
        "local_only": True,   # HARD LOCK: no remote calls
    }

    tasks = load_tasks(limit=args.limit)

    console.success(f"{len(tasks)} task(s) loaded")

    for task in tasks:
        console.info(f"\nRunning task: {task['task_id']}")

        try:
            console.step("Preparing snapshot...")
            console.success("Snapshot ready")

            console.step("Generating patch (local LLM)...")

            result = run_experiment(config, [task])

            if result.get("passed", False):
                console.success("TASK PASSED")
            else:
                console.warn("TASK FAILED")

        except Exception as e:
            console.error(str(e))


if __name__ == "__main__":
    main()