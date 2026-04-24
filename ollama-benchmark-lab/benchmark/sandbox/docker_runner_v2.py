"""
Docker-based sandbox execution runner for SWE-bench tasks.

This module provides the DockerRunnerV2 class, which securely clones repositories
and applies code patches inside a temporary directory for sandbox execution.

Example:
    >>> runner = DockerRunnerV2()
    >>> result = runner.run({"repo_url": "https://github.com/foo/bar.git"})
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from benchmark.patch.engine import PatchEngine


class DockerRunnerV2:
    """
    Sandbox runner for managing SWE-bench tasks within Docker.

    Attributes:
        patch_engine (PatchEngine): Engine responsible for applying text patches.
    """

    def __init__(self, patch_engine: Optional[PatchEngine] = None) -> None:
        """
        Initialize the DockerRunnerV2 instance.

        Args:
            patch_engine (Optional[PatchEngine]): An existing PatchEngine instance.
                If None is provided, a new instance is created automatically.
        """
        self.patch_engine: PatchEngine = patch_engine or PatchEngine()

    def run(self, task: Dict[str, Any]) -> Dict[str, str]:
        """
        Execute a task by cloning its repository and applying its patch.

        Args:
            task (Dict[str, Any]): A dictionary containing task parameters such as
                'repo_url', 'snapshot_path', and 'patch'.

        Returns:
            Dict[str, str]: A dictionary containing the 'repo_path' of the prepared environment.

        Raises:
            RuntimeError: If 'repo_url' is missing in the task payload.
        """
        repo_url: Optional[str] = task.get("repo_url")

        if not repo_url:
            raise RuntimeError("Task missing repo_url")

        repo_path_raw: Optional[str] = task.get("snapshot_path")

        repo_path: Path
        if repo_path_raw:
            repo_path = Path(repo_path_raw)
        else:
            repo_path = self._clone_repo(repo_url)

        patch_text: str = task.get("patch") or ""

        # Apply the patch using the patch engine
        repo_path = self.patch_engine.apply_patch(repo_path, patch_text)

        return {"repo_path": str(repo_path)}

    def _clone_repo(self, repo_url: str) -> Path:
        """
        Safely clone a git repository in a non-interactive mode.

        Args:
            repo_url (str): The URL of the repository to clone.

        Returns:
            Path: The path to the temporary directory containing the cloned repository.

        Raises:
            RuntimeError: If the git clone subprocess fails.
        """
        tmp_dir: Path = Path(tempfile.mkdtemp(prefix="swebench_"))

        env: Dict[str, str] = os.environ.copy()

        # FORCE NON-INTERACTIVE MODE
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GCM_INTERACTIVE"] = "never"
        env["GIT_ASKPASS"] = "echo"

        cmd = [
            "git",
            "clone",
            "--depth",
            "1",
            repo_url,
            str(tmp_dir),
        ]

        proc = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
        )

        if proc.returncode != 0:
            raise RuntimeError(
                "Git clone failed (non-interactive mode enforced)\n\n"
                f"STDERR:\n{proc.stderr.strip()}\n\n"
                "Hint: ensure repo_url is public or cached locally."
            )

        return tmp_dir