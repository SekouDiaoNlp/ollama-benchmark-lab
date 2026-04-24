"""
Docker-based sandbox execution for benchmark tasks.

This module provides the DockerRunner class for executing test commands
within isolated Docker containers.
"""

import subprocess
import uuid
from typing import Any, Dict, Union
from pathlib import Path

# Canonical sandbox image
IMAGE: str = "swe-sandbox:latest"

class DockerRunner:
    """
    Executes commands within a Docker container sandbox.
    """

    def run_tests(
        self, 
        repo_path: Union[str, Path], 
        cmd: str = "pytest -q", 
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Execute a test command in a Docker container with the repository mounted.

        Args:
            repo_path (Union[str, Path]): Path to the local repository.
            cmd (str): Command to execute in the container.
            timeout (int): Maximum execution time in seconds.

        Returns:
            Dict[str, Any]: Execution status and captured output.
        """
        container_name: str = f"swe_{uuid.uuid4().hex[:8]}"

        try:
            # Mount host repo_path to container /workspace
            subprocess.run([
                "docker", "run", "--rm",
                "--name", container_name,
                "-v", f"{Path(repo_path).resolve()}:/workspace",
                IMAGE,
                "bash", "-lc", cmd
            ], timeout=timeout, check=True, capture_output=True)

            return {"status": "pass"}

        except subprocess.CalledProcessError as e:
            return {
                "status": "fail",
                "stdout": e.stdout.decode() if e.stdout else "",
                "stderr": e.stderr.decode() if e.stderr else ""
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "stderr": f"Execution exceeded {timeout}s"
            }