#!/usr/bin/env python3
"""
Benchmark runner module for executing the SWE and PLAN/ACT tasks.

This module provides the main `BenchmarkRunner` loop to iterate over models and tasks,
score the results, and persist progress using heartbeats and checkpoints.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any

from benchmark.ollama_client import OllamaClient
from benchmark.checkpoint import CheckpointManager
from benchmark.evaluator import RealEvaluator


# =========================================================
# PATHS
# =========================================================

ROOT: Path = Path(__file__).resolve().parents[1]
RESULTS_DIR: Path = ROOT / "results"
STATE_FILE: Path = RESULTS_DIR / "state.jsonl"
RESULTS_DIR.mkdir(exist_ok=True, parents=True)


# =========================================================
# MODEL SELECTION
# =========================================================

def get_models(mode: str) -> List[str]:
    """
    Retrieve available models from the local Ollama instance.

    Args:
        mode (str): A filter string (e.g., 'noyap' or 'all').

    Returns:
        List[str]: A sorted list of model names.
    """
    import subprocess

    raw: str = subprocess.check_output(["ollama", "list"], text=True)
    lines: List[str] = raw.splitlines()[1:]

    models: List[str] = []
    for line in lines:
        if not line.strip():
            continue
        name: str = line.split()[0]

        if mode == "noyap":
            if "noyap" in name:
                models.append(name)
        else:
            models.append(name)

    return sorted(models)


# =========================================================
# TASK LOADING
# =========================================================

def load_tasks(cfg: Dict[str, Any], smoke: bool = False) -> List[Dict[str, Any]]:
    """
    Load task definitions from JSON files in the `tasks` directory.

    Args:
        cfg (Dict[str, Any]): Configuration dictionary (currently unused but kept for API compat).
        smoke (bool): If True, returns only a subset of tasks for quick testing.

    Returns:
        List[Dict[str, Any]]: A list of task dictionaries.
    """
    task_root: Path = Path("tasks")
    tasks: List[Dict[str, Any]] = []

    for path in task_root.glob("**/*.json"):
        try:
            data: Any = json.loads(path.read_text())

            if isinstance(data, dict):
                data = [data]

            for t in data:
                if smoke and len(tasks) >= 2:
                    return tasks

                tasks.append(t)

        except Exception:
            continue

    return tasks


# =========================================================
# HEARTBEAT
# =========================================================

def heartbeat(model: str, task_id: str) -> None:
    """
    Write a heartbeat timestamp to disk to indicate active processing.

    Args:
        model (str): The current model being evaluated.
        task_id (str): The current task identifier.
    """
    (RESULTS_DIR / "heartbeat.txt").write_text(
        json.dumps({
            "model": model,
            "task": task_id,
            "ts": time.time()
        })
    )


# =========================================================
# RESULT STRUCT
# =========================================================

@dataclass
class RunResult:
    """
    Data structure representing the outcome of a single task run.

    Attributes:
        model (str): The name of the model.
        task_id (str): The identifier of the task.
        score (float): The final score of the evaluation.
        latency_s (float): The total execution time in seconds.
    """
    model: str
    task_id: str
    score: float
    latency_s: float


# =========================================================
# BENCHMARK RUNNER
# =========================================================

class BenchmarkRunner:
    """
    Orchestrates the evaluation of multiple models against multiple tasks.

    Attributes:
        client (OllamaClient): The local inference client.
        evaluator (RealEvaluator): The scoring logic for evaluation.
        ckpt (CheckpointManager): The state persistence manager.
    """

    def __init__(self, client: OllamaClient, evaluator: RealEvaluator, ckpt: CheckpointManager) -> None:
        """
        Initialize the BenchmarkRunner.

        Args:
            client (OllamaClient): The LLM client.
            evaluator (RealEvaluator): The semantic and execution evaluator.
            ckpt (CheckpointManager): The checkpoint persistence manager.
        """
        self.client: OllamaClient = client
        self.evaluator: RealEvaluator = evaluator
        self.ckpt: CheckpointManager = ckpt

    def _get_prompt(self, task: Dict[str, Any]) -> str:
        """
        Extract the best available prompt from a task dictionary.

        Args:
            task (Dict[str, Any]): The task definition.

        Returns:
            str: The extracted prompt.
        """
        if "public_prompt" in task:
            return str(task["public_prompt"])
        return str(task.get("prompt", ""))

    def run_task(self, model: str, task: Dict[str, Any]) -> RunResult:
        """
        Execute a single task against a single model.

        Args:
            model (str): The target model name.
            task (Dict[str, Any]): The target task dictionary.

        Returns:
            RunResult: The latency and score results.
        """
        task_id: str = str(task.get("id", "unknown"))
        heartbeat(model, task_id)

        prompt: str = self._get_prompt(task)

        start: float = time.time()

        output: str = self.client.run(
            model=model,
            prompt=prompt
        )

        latency: float = time.time() - start
        score: float = self.evaluator.score(task, output)

        return RunResult(
            model=model,
            task_id=task_id,
            score=score,
            latency_s=latency
        )

    def run(self, models: List[str], tasks: List[Dict[str, Any]], resume: bool) -> None:
        """
        Run the full matrix of models and tasks.

        Args:
            models (List[str]): List of models to evaluate.
            tasks (List[Dict[str, Any]]): List of tasks to run.
            resume (bool): If True, skips previously completed runs using the checkpoint cache.
        """
        for model in models:
            for task in tasks:
                task_id: str = str(task.get("id", "unknown"))
                key: str = f"{model}::{task_id}"

                if resume and self.ckpt.done(key):
                    continue

                try:
                    result: RunResult = self.run_task(model, task)
                    self.ckpt.save(key, asdict(result))

                except Exception as e:
                    self.ckpt.save(key, {
                        "model": model,
                        "task_id": task_id,
                        "error": str(e)
                    })


# =========================================================
# CLI
# =========================================================

def main() -> None:
    """
    Entry point for running the benchmark directly from the CLI.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["all", "noyap"], default="all")
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--resume", action="store_true")

    args = parser.parse_args()

    ckpt = CheckpointManager(STATE_FILE)
    client = OllamaClient()
    evaluator = RealEvaluator()

    runner = BenchmarkRunner(client, evaluator, ckpt)

    models: List[str] = get_models(args.mode)
    tasks: List[Dict[str, Any]] = load_tasks({}, smoke=args.smoke_test)

    print("\n==============================")
    print("OLLAMA BENCHMARK (SWE MODE)")
    print("==============================\n")

    runner.run(models, tasks, args.resume)

    print("\nDONE")


if __name__ == "__main__":
    main()