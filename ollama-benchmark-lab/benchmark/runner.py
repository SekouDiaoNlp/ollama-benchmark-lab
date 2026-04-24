#!/usr/bin/env python3
"""
Ollama Benchmark Runner (vNEXT++)

Fixes:
- smoke test now uses ONLY fastest models (not full model set)
- introduces model profiling cache
- prevents long-running smoke execution
- enforces deterministic fast-path fallback
"""

from __future__ import annotations

import argparse
import json
import time
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional

from benchmark.ollama_client import OllamaClient
from benchmark.checkpoint import CheckpointManager
from benchmark.evaluator import RealEvaluator
from benchmark.utils import load_config


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True, parents=True)

STATE_FILE = RESULTS_DIR / "state.jsonl"
HEARTBEAT_FILE = RESULTS_DIR / "heartbeat.txt"

MODEL_CACHE_FILE = RESULTS_DIR / "model_profile_cache.json"


# =========================================================
# TASK LOADING
# =========================================================

def load_tasks(cfg: Dict[str, Any], smoke: bool = False) -> List[Dict[str, Any]]:
    """
    Robust recursive task loader:
    - supports tasks/plan, tasks/act, tasks/swe
    - case normalizes mode
    - smoke-safe slicing
    """

    import json
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    task_dir = ROOT / "tasks"

    if not task_dir.exists():
        print(f"⚠ tasks directory not found: {task_dir}")
        return []

    tasks = []

    # 🔥 FIX: recursive search
    for file in task_dir.rglob("*.json"):

        try:
            task = json.loads(file.read_text())

            # normalize mode
            if "mode" in task:
                task["mode"] = task["mode"].upper()

            # optional: infer mode from folder if missing
            if "mode" not in task:
                if "plan" in str(file).lower():
                    task["mode"] = "PLAN"
                elif "act" in str(file).lower():
                    task["mode"] = "ACT"
                elif "swe" in str(file).lower():
                    task["mode"] = "SWE"

            tasks.append(task)

        except Exception as e:
            print(f"⚠ Failed loading {file}: {e}")

    if smoke:
        return tasks[:2]

    mode = cfg.get("tasks", {}).get("mode", "all").upper()

    if mode == "ALL":
        return tasks

    return [t for t in tasks if t.get("mode", "").upper() == mode]


# =========================================================
# MODEL SELECTION + PROFILING CACHE
# =========================================================

def _get_all_models() -> List[str]:
    raw = subprocess.check_output(["ollama", "list"], text=True)
    lines = raw.splitlines()[1:]

    models = []
    for line in lines:
        if not line.strip():
            continue
        models.append(line.split()[0])

    return models


def _load_model_cache() -> Optional[Dict[str, float]]:
    if MODEL_CACHE_FILE.exists():
        return json.loads(MODEL_CACHE_FILE.read_text())
    return None


def _save_model_cache(data: Dict[str, float]):
    MODEL_CACHE_FILE.write_text(json.dumps(data, indent=2))


def _default_fast_models(all_models: List[str]) -> List[str]:
    """
    deterministic fallback if no cache exists
    """
    preferred = [
        "codegemma:2b-acting-noyap",
        "starcoder2:3b-acting-noyap",
    ]

    return [m for m in preferred if m in all_models][:2]


def filter_models(cfg: Dict[str, Any], smoke: bool = False) -> List[str]:
    all_models = _get_all_models()

    # normal mode
    if not smoke:
        if cfg["model_selection"]["mode"] == "noyap_only":
            return [m for m in all_models if "noyap" in m]
        return all_models

    # =========================
    # SMOKE MODE FIX
    # =========================

    cache = _load_model_cache()

    if cache:
        # sort by latency ascending
        sorted_models = sorted(cache.items(), key=lambda x: x[1])
        return [m for m, _ in sorted_models[:2]]

    # fallback if no cache
    return _default_fast_models(all_models)


# =========================================================
# HEARTBEAT
# =========================================================

def write_heartbeat(model: str, task_id: str):
    HEARTBEAT_FILE.write_text(json.dumps({
        "timestamp": time.time(),
        "model": model,
        "task": task_id
    }))


# =========================================================
# RUNNER
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
        self.evaluator = RealEvaluator()

    def run_task(self, model: str, task: Dict[str, Any]) -> RunResult:

        write_heartbeat(model, task["id"])

        start = time.time()
        output = self.client.run(model=model, prompt=task["prompt"])
        latency = time.time() - start

        score = self.evaluator.score(task, output)

        return RunResult(
            model=model,
            task_id=task["id"],
            mode=task["mode"],
            success=True,
            latency_s=latency,
            output_chars=len(output),
            score=score
        )

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

    cfg = load_config()

    parser = argparse.ArgumentParser()

    parser.add_argument("--mode", choices=["all", "noyap"], default="all")
    parser.add_argument("--tasks", choices=["plan", "act", "all"], default="all")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")

    args = parser.parse_args()

    ckpt = CheckpointManager(STATE_FILE)
    client = OllamaClient()

    runner = BenchmarkRunner(client, ckpt)

    models = filter_models(cfg, smoke=args.smoke_test)
    tasks = load_tasks(cfg, smoke=args.smoke_test)

    print(f"""
==============================
OLLAMA BENCHMARK vNEXT++
MODE: {'SMOKE' if args.smoke_test else 'FULL'}
Models: {len(models)}
Tasks:  {len(tasks)}
==============================
""")

    runner.run(models, tasks, args.resume)

    print("\nDONE")


if __name__ == "__main__":
    main()