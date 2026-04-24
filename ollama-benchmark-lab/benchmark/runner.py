#!/usr/bin/env python3
"""
Ollama Benchmark Runner (vNEXT - SWE-BENCH COMPATIBLE)

Changes:
- supports public_prompt (SWE format)
- fallback to legacy prompt
- passes rubric to evaluator
- task format hardened
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
from benchmark.utils import load_config


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"

STATE_FILE = RESULTS_DIR / "state.jsonl"
RESULTS_DIR.mkdir(exist_ok=True, parents=True)


# =========================================================
# MODEL SELECTION
# =========================================================

def get_models(mode: str) -> List[str]:
    import subprocess

    raw = subprocess.check_output(["ollama", "list"], text=True)
    lines = raw.splitlines()[1:]

    models = []
    for line in lines:
        if not line.strip():
            continue
        name = line.split()[0]

        if mode == "noyap":
            if "noyap" in name:
                models.append(name)
        else:
            models.append(name)

    return sorted(models)


# =========================================================
# TASK LOADING (SWE COMPAT)
# =========================================================

def load_tasks(cfg: Dict[str, Any], smoke: bool = False) -> List[Dict[str, Any]]:
    """
    Loads tasks from tasks/ or tasks_swe/
    Supports SWE format + legacy format.
    """

    task_root = Path("tasks")

    tasks: List[Dict[str, Any]] = []

    for path in task_root.glob("**/*.json"):
        try:
            data = json.loads(path.read_text())

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

def heartbeat(model: str, task_id: str):
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
    model: str
    task_id: str
    score: float
    latency_s: float


# =========================================================
# RUNNER
# =========================================================

class BenchmarkRunner:

    def __init__(self, client: OllamaClient, evaluator: RealEvaluator, ckpt: CheckpointManager):
        self.client = client
        self.evaluator = evaluator
        self.ckpt = ckpt

    def _get_prompt(self, task: Dict[str, Any]) -> str:
        # SWE-bench style
        if "public_prompt" in task:
            return task["public_prompt"]

        # legacy fallback
        return task.get("prompt", "")

    def run_task(self, model: str, task: Dict[str, Any]) -> RunResult:

        heartbeat(model, task.get("id", "unknown"))

        prompt = self._get_prompt(task)

        start = time.time()

        output = self.client.run(
            model=model,
            prompt=prompt
        )

        latency = time.time() - start

        score = self.evaluator.score(task, output)

        return RunResult(
            model=model,
            task_id=task.get("id", "unknown"),
            score=score,
            latency_s=latency
        )

    def run(self, models: List[str], tasks: List[Dict[str, Any]], resume: bool):

        for model in models:
            for task in tasks:

                key = f"{model}::{task.get('id')}"

                if resume and self.ckpt.done(key):
                    continue

                try:
                    result = self.run_task(model, task)

                    self.ckpt.save(key, asdict(result))

                except Exception as e:
                    self.ckpt.save(key, {
                        "model": model,
                        "task_id": task.get("id"),
                        "error": str(e)
                    })


# =========================================================
# CLI
# =========================================================

def main():

    cfg = load_config()

    parser = argparse.ArgumentParser()

    parser.add_argument("--mode", choices=["all", "noyap"], default="all")
    parser.add_argument("--tasks", choices=["all"], default="all")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")

    args = parser.parse_args()

    ckpt = CheckpointManager(STATE_FILE)
    client = OllamaClient()
    evaluator = RealEvaluator()

    runner = BenchmarkRunner(client, evaluator, ckpt)

    models = get_models(args.mode)
    tasks = load_tasks(cfg, smoke=args.smoke_test)

    print("\n==============================")
    print("OLLAMA BENCHMARK (SWE MODE)")
    print(f"Models: {len(models)}")
    print(f"Tasks:  {len(tasks)}")
    print("==============================\n")

    runner.run(models, tasks, args.resume)

    print("\nDONE")


if __name__ == "__main__":
    main()