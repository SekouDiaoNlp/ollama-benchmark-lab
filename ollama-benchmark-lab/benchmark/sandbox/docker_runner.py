import subprocess
import uuid
from pathlib import Path

IMAGE = "swe-sandbox:latest"


def run_in_container(repo_path: Path, command: str, timeout: int = 300):
    container_id = f"swe_{uuid.uuid4().hex[:8]}"

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "--name", container_id,
                "-v", f"{repo_path}:/workspace",
                IMAGE,
                "bash", "-lc", command
            ],
            text=True,
            capture_output=True,
            timeout=timeout
        )

        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "stdout": "",
            "stderr": "Execution timed out"
        }