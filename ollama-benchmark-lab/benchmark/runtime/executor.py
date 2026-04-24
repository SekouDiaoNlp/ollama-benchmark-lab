"""
Core task execution runtime for SWE-bench evaluations.

This module provides the `run_task` function, which manages repository snapshotting,
patch application, and Docker sandbox execution for a given task.

Example:
    >>> from benchmark.runtime.executor import run_task
    >>> result = run_task({"id": "task1", "repo": "foo/bar", "base_commit": "HEAD", "execution": {"entrypoint": "pytest"}})
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from benchmark.runtime.repo_snapshot import RepoSnapshot
from benchmark.runtime.patch_engine import PatchEngine
from benchmark.sandbox.docker_runner_v2 import DockerRunnerV2

logger = logging.getLogger(__name__)

# Global instances for the runtime lifecycle
repo_snapshot = RepoSnapshot()
patch_engine = PatchEngine()
docker = DockerRunnerV2()


def run_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an individual task by preparing its repository and running it in Docker.

    Args:
        task (Dict[str, Any]): The task payload containing the repository, commit,
            optional patch, and execution entrypoint.

    Returns:
        Dict[str, Any]: The task result containing its ID and the Docker execution output.

    Raises:
        RuntimeError: If the repository snapshot is missing or the path is invalid.
    """
    task_id: str = str(task.get("id", "unknown"))
    logger.debug("[EXECUTOR DEBUG] TASK ID=%s", task_id)

    repo: Path = repo_snapshot.get(str(task["repo"]), str(task["base_commit"]))

    logger.debug("[EXECUTOR DEBUG] repo type=%s value=%s", type(repo), repo)

    if repo is None:
        raise RuntimeError("Missing repo snapshot")

    patch_text: Optional[str] = task.get("patch")
    if patch_text:
        patch_engine.apply(repo, patch_text)

    logger.debug("[EXECUTOR DEBUG] BEFORE EXISTS CHECK type=%s value=%s", type(repo), repo)

    repo_path: Path = Path(repo)

    logger.debug("[EXECUTOR DEBUG] AFTER PATH WRAP type=%s value=%s", type(repo_path), repo_path)

    if not repo_path.exists():
        logger.error("[EXECUTOR DEBUG] INVALID PATH: %s", repo_path)
        raise RuntimeError(f"Invalid repo path resolved: {repo}")

    result: Any = docker.run(
        repo_path=repo_path,
        command=task["execution"]["entrypoint"]
    )  # type: ignore

    return {
        "id": task_id,
        "result": result
    }