# benchmark/sandbox/docker_runner.py

import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any


def run_in_sandbox(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal SWE-bench style execution sandbox.

    Simulates:
    - isolated repo execution
    - pytest run
    """

    repo_path = Path(task.get("repo_path", "."))

    test_path = task["tests"]["path"]

    cmd = [
        "pytest",
        "-q",
        test_path
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "status": "ok" if proc.returncode == 0 else "fail",
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "passed": proc.returncode == 0,
        }

    except Exception as e:
        return {
            "status": "error",
            "stdout": "",
            "stderr": str(e),
            "passed": False,
        }