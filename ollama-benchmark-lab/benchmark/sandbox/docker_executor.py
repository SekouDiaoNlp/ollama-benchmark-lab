from __future__ import annotations

import subprocess
import tempfile
import shutil
import uuid
from pathlib import Path
from typing import Dict, Any


class DockerExecutor:
    """
    Executes model-generated code in isolated Docker container
    and runs pytest against hidden tests.
    """

    def __init__(self, timeout: int = 120):
        self.timeout = timeout

    def run(self, code: str, task: Dict[str, Any]) -> Dict[str, Any]:
        task_id = task["id"]

        tmp_dir = Path(tempfile.mkdtemp(prefix=f"sandbox_{task_id}_"))
        container_name = f"sandbox_{uuid.uuid4().hex[:8]}"

        try:
            # -----------------------------------------
            # 1. Write generated code
            # -----------------------------------------
            code_file = tmp_dir / "solution.py"
            code_file.write_text(code)

            # -----------------------------------------
            # 2. Copy hidden tests
            # -----------------------------------------
            tests_src = Path("tasks") / task["mode"].lower() / task_id / "tests"

            if tests_src.exists():
                shutil.copytree(tests_src, tmp_dir / "tests")
            else:
                return {
                    "success": False,
                    "error": "missing_tests"
                }

            # -----------------------------------------
            # 3. Create minimal runner script
            # -----------------------------------------
            (tmp_dir / "run.sh").write_text(
                """
pip install pytest >/dev/null 2>&1
pytest -q --disable-warnings --maxfail=1
"""
            )

            # -----------------------------------------
            # 4. Docker run
            # -----------------------------------------
            cmd = [
                "docker", "run", "--rm",
                "--name", container_name,
                "-v", f"{tmp_dir.absolute()}:/app",
                "-w", "/app",
                "python:3.11-slim",
                "bash", "run.sh"
            ]

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            stdout = proc.stdout
            stderr = proc.stderr

            passed = proc.returncode == 0

            return {
                "success": True,
                "passed": passed,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": proc.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "timeout"
            }

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)