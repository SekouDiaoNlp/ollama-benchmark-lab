import subprocess
import uuid

IMAGE = "swe-sandbox:latest"

class DockerRunner:

    def run_tests(self, repo_path, cmd="pytest -q", timeout=120):
        container = f"swe_{uuid.uuid4().hex[:8]}"

        try:
            subprocess.run([
                "docker", "run", "--rm",
                "--name", container,
                "-v", f"{repo_path}:/workspace",
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