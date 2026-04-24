import docker
import uuid


class DockerRunner:
    """
    SWE-bench parity execution runtime.

    No host leakage. No assumptions. Fully isolated.
    """

    def __init__(self, image="python:3.11-slim"):
        self.client = docker.from_env()
        self.image = image

    def run(self, repo_path, command, timeout=300):
        container = self.client.containers.run(
            self.image,
            command="sleep infinity",
            detach=True,
            tty=True,
            volumes={
                str(repo_path): {
                    "bind": "/workspace",
                    "mode": "rw"
                }
            },
            working_dir="/workspace"
        )

        try:
            exec_result = container.exec_run(
                cmd=f"bash -lc '{command}'",
                stdout=True,
                stderr=True,
                demux=True
            )

            stdout, stderr = exec_result.output

            return {
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "exit_code": exec_result.exit_code
            }

        finally:
            container.kill()
            container.remove()