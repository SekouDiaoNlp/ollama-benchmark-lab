#!/usr/bin/env python3
"""
Ollama Benchmark Runner (vNEXT)

Key properties:
- crash-safe / sleep-safe via checkpointing
- resumable runs
- PLAN / ACT evaluation modes
- model filtering (ALL vs NOYAP only)
- smoke-test mode (infrastructure validation)
- heartbeat + watchdog integration ready
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional

from benchmark.ollama_client import OllamaClient
from benchmark.checkpoint import CheckpointManager
from benchmark.state import RunState
from benchmark.evaluator import SimpleEvaluator


# =========================================================
# CONFIG PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"

STATE_FILE = RESULTS_DIR / "state.jsonl"
RESULTS_FILE = RESULTS_DIR / "results.jsonl"
HEARTBEAT_FILE = RESULTS_DIR / "heartbeat.txt"

RESULTS_DIR.mkdir(exist_ok=True, parents=True)


# =========================================================
# TASK DEFINITIONS (PLAN / ACT)
# at least 30–80 LOC each requirement satisfied elsewhere in tasks/
# =========================================================

PLAN_TASKS = [
    {
        "id": "plan_sorting_optimizer",
        "mode": "PLAN",
        "prompt": """
Design a system that selects the optimal sorting algorithm at runtime.

Constraints:
- Must support arrays up to 10^7 elements
- Must detect nearly-sorted input
- Must switch between quicksort, mergesort, insertion sort
- Must be fully typed
- Must include benchmarking hooks

Return only Python code.
"""
    },
    {
        "id": "plan_ast_pipeline",
        "mode": "PLAN",
        "prompt": """
Design a Python AST transformation pipeline that:

- parses Python source code
- applies a sequence of transforms
- supports plugin architecture
- logs transformations
- is testable with pytest

Return full typed implementation.
"""
    }
]

ACT_TASKS = [
    {
        "id": "act_palindrome",
        "mode": "ACT",
        "prompt": """
Write a fully typed Python module that:
- checks if a string is a palindrome
- ignores punctuation and case
- supports Unicode normalization
- includes a pytest test suite
- includes CLI entrypoint

Return full code.
"""
    },
    {
        "id": "act_patch_refactor",
        "mode": "ACT",
        "prompt": """
Given a buggy function (assume provided), produce a PATCH-style fix:

Requirements:
- output unified diff format
- fix type issues
- improve performance
- add missing tests
- must not rewrite unrelated code

Return ONLY the patch.
"""
    }
]


# =========================================================
# MODEL FILTERING
# =========================================================

def get_models(mode: str) -> List[str]:
    """
    mode:
      - all
      - noyap
    """
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
# HEARTBEAT SYSTEM
# =========================================================

def write_heartbeat(model: str, task_id: str):
    HEARTBEAT_FILE.write_text(
        json.dumps({
            "timestamp": time.time(),
            "model": model,
            "task": task_id
        })
    )


# =========================================================
# MAIN RUNNER
# =========================================================

@dataclass
class RunResult:
    model: str
    task_id: str
    mode: str
    success: bool
    latency_s: float
    output_chars: int
    score: float


class BenchmarkRunner:

    def __init__(self, client: OllamaClient, ckpt: CheckpointManager):
        self.client = client
        self.ckpt = ckpt
        self.evaluator = SimpleEvaluator()

    def run_task(self, model: str, task: Dict[str, Any]) -> RunResult:

        write_heartbeat(model, task["id"])

        start = time.time()

        output = self.client.run(
            model=model,
            prompt=task["prompt"]
        )

        latency = time.time() - start

        score = self.evaluator.score(task, output)

        result = RunResult(
            model=model,
            task_id=task["id"],
            mode=task["mode"],
            success=True,
            latency_s=latency,
            output_chars=len(output),
            score=score
        )

        return result

    def run(self, models: List[str], tasks: List[Dict[str, Any]], resume: bool):

        for model in models:
            for task in tasks:

                key = f"{model}::{task['id']}"

                if resume and self.ckpt.done(key):
                    continue

                try:
                    result = self.run_task(model, task)

                    self.ckpt.save(key, asdict(result))

                except Exception as e:
                    self.ckpt.save(key, {
                        "model": model,
                        "task_id": task["id"],
                        "error": str(e)
                    })


# =========================================================
# CLI
# =========================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--mode", choices=["all", "noyap"], default="all")
    parser.add_argument("--tasks", choices=["plan", "act", "all"], default="all")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")

    args = parser.parse_args()

    ckpt = CheckpointManager(STATE_FILE)
    client = OllamaClient()

    runner = BenchmarkRunner(client, ckpt)

    models = get_models(args.mode)

    if args.smoke_test:
        print("🧪 SMOKE TEST MODE")
        models = models[:2]
        tasks = PLAN_TASKS[:1] + ACT_TASKS[:1]
    else:
        if args.tasks == "plan":
            tasks = PLAN_TASKS
        elif args.tasks == "act":
            tasks = ACT_TASKS
        else:
            tasks = PLAN_TASKS + ACT_TASKS

    print(f"""
==============================
OLLAMA BENCHMARK vNEXT
Models: {len(models)}
Tasks:  {len(tasks)}
Mode:   {args.mode}
Resume: {args.resume}
Smoke:  {args.smoke_test}
==============================
""")

    runner.run(models, tasks, args.resume)

    print("\nDONE")


if __name__ == "__main__":
    main()