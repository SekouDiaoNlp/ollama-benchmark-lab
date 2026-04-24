import docker
import uuid


class DockerRunner:
    """
    Isolated execution environment for SWE-bench tasks.
    """

    def __init__(self, image="python:3.11-slim"):
        self.client = docker.from_env()
        self.image = image

    def run(self, repo_path, command):
        container_name = f"swe_{uuid.uuid4().hex[:8]}"

        container = self.client.containers.run(
            self.image,
            command="/bin/bash",
            name=container_name,
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
            exec_log = container.exec_run(command, stdout=True, stderr=True)
            output = exec_log.output.decode()

            return {
                "status": "success",
                "output": output
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

        finally:
            container.kill()
            container.remove()