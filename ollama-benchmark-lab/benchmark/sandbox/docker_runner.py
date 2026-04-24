import docker
import tempfile
import shutil
import subprocess
from pathlib import Path
import os


class DockerRunner:
    """
    Minimal SWE-bench style execution sandbox.
    """

    def __init__(self, image="python:3.11-slim"):
        self.client = docker.from_env()
        self.image = image

    def run(self, repo_path: str, command: str, timeout: int = 300):
        """
        Execute a command inside a Docker container with repo mounted.
        """

        repo_path = str(Path(repo_path).resolve())

        container = self.client.containers.run(
            image=self.image,
            command=["bash", "-lc", command],
            volumes={
                repo_path: {"bind": "/workspace", "mode": "rw"}
            },
            working_dir="/workspace",
            detach=True,
            stderr=True,
            stdout=True,
            network_disabled=True,
            mem_limit="2g"
        )

        try:
            result = container.wait(timeout=timeout)
            logs = container.logs().decode("utf-8")

            return {
                "exit_code": result.get("StatusCode", 1),
                "logs": logs,
                "status": "finished"
            }

        except Exception as e:
            container.kill()
            return {
                "exit_code": -1,
                "logs": str(e),
                "status": "timeout_or_error"
            }

        finally:
            container.remove(force=True)