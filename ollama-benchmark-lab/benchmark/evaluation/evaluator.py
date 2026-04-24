"""
SWE-Bench Style Evaluator (Docker + Pytest + Rubric Scoring)
Updated for task schema v2

Key changes:
- task["tests"]["path"] supported
- task["execution"]["entrypoint"] supported
- fallback compatibility with legacy fields
- docker sandbox execution
- pytest-based scoring
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Tuple


# -----------------------------
# Config
# -----------------------------

DOCKER_IMAGE = "swe-sandbox:latest"
DEFAULT_TIMEOUT = 30


# -----------------------------
# Utilities
# -----------------------------


def _run(cmd: list[str], timeout: int = DEFAULT_TIMEOUT) -> Tuple[int, str, str]:
    """Run local subprocess (fallback mode)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"


# -----------------------------
# Docker Sandbox Runner
# -----------------------------


def run_in_docker(workdir: Path, cmd: list[str], timeout: int = DEFAULT_TIMEOUT) -> Tuple[int, str, str]:
    """
    Execute command inside Docker sandbox.
    """
    abs_path = str(workdir.resolve())

    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{abs_path}:/workspace",
        "-w", "/workspace",
        DOCKER_IMAGE,
        "bash", "-lc", " ".join(cmd)
    ]

    return _run(docker_cmd, timeout=timeout)


# -----------------------------
# Task Loader
# -----------------------------


def load_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize task format (v2 + backward compatibility)
    """

    execution = task.get("execution", {})

    task["_tests_path"] = (
        task.get("tests", {}).get("path")
        or task.get("tests")
        or "tests"
    )

    task["_entrypoint"] = (
        execution.get("entrypoint")
        or task.get("entrypoint")
        or "pytest"
    )

    return task


# -----------------------------
# Pytest Execution
# -----------------------------


def run_pytest(task_dir: Path, test_path: str) -> Tuple[bool, str]:
    """
    Run pytest inside sandbox.
    """
    cmd = ["pytest", test_path, "-q", "--disable-warnings"]

    code, out, err = run_in_docker(task_dir, cmd)

    success = code == 0
    return success, out + "\n" + err


# -----------------------------
# Evaluation Core
# -----------------------------


def evaluate_task(task: Dict[str, Any], solution_path: Path) -> Dict[str, Any]:
    """
    Evaluate a single SWE task.
    """

    task = load_task(task)

    task_id = task["id"]
    test_path = task["_tests_path"]

    task_dir = solution_path / task_id

    start = time.time()

    passed, logs = run_pytest(task_dir, test_path)

    duration = time.time() - start

    rubric = task.get("rubric", {})

    score = 0.0

    if passed:
        score += rubric.get("correctness", 1.0)
    else:
        score += 0.0

    # lightweight heuristics
    if "edge" in logs.lower():
        score += rubric.get("edge_cases", 0.0) * 0.5

    return {
        "task_id": task_id,
        "passed": passed,
        "score": min(score, 1.0),
        "duration": duration,
        "logs": logs[-2000:],
    }


# -----------------------------
# Batch Evaluation
# -----------------------------


def evaluate_all(tasks: list[Dict[str, Any]], solutions_dir: str) -> Dict[str, Any]:
    results = []

    for task in tasks:
        res = evaluate_task(task, Path(solutions_dir))
        results.append(res)

    avg_score = sum(r["score"] for r in results) / len(results)

    return {
        "results": results,
        "avg_score": avg_score,
        "count": len(results),
    }


# -----------------------------
# CLI
# -----------------------------


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--solutions", required=True)

    args = parser.parse_args()

    tasks = json.load(open(args.tasks))

    report = evaluate_all(tasks, args.solutions)

    print(json.dumps(report, indent=2))
