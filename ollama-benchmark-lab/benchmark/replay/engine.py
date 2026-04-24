"""
Task replay and execution engine.

This module provides the ReplayEngine class which orchestrates repository
management, patch application, and sandbox execution.
"""

from typing import Any, Dict
from benchmark.replay.repo_manager import RepoManager
from benchmark.replay.patcher import apply_patch
from benchmark.replay.docker_runner import DockerRunner

class ReplayEngine:
    """
    Orchestrates the replay of benchmark tasks.

    Attributes:
        repos (RepoManager): Manager for repository checkouts.
        runner (DockerRunner): Executor for sandbox runs.
    """

    def __init__(self) -> None:
        """
        Initialize the replay engine components.
        """
        self.repos: RepoManager = RepoManager()
        self.runner: DockerRunner = DockerRunner()

    def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replay a single benchmark task.

        Args:
            task (Dict[str, Any]): The task configuration.

        Returns:
            Dict[str, Any]: The task identifier and execution result.
        """
        repo_url: str = str(task.get("repo", ""))
        repo_path = self.repos.get_repo(repo_url)

        patch_text: str = str(task.get("patch", ""))
        apply_patch(repo_path, patch_text)

        # Ensure execution block exists with defaults
        execution: Dict[str, Any] = task.get("execution", {})
        entrypoint: str = execution.get("entrypoint", "pytest -q")

        result = self.runner.run_tests(
            repo_path,
            cmd=entrypoint
        )

        return {
            "id": task.get("id"),
            "result": result
        }
    
    def run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Backward compatibility alias for run()."""
        return self.run(task)