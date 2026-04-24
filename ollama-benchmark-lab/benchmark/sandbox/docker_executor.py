from __future__ import annotations

import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import Dict, Any


class DockerExecutor:
    """
    Executes untrusted code inside a Docker sandbox.
    - timeout enforced
    - stdout/stderr captured
    - no host filesystem access
    """

    IMAGE = "python:3.12-slim"

    def run(self, code: str, tests: str | None = None, timeout: int = 5) -> Dict[str, Any]:

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            # write solution
            (tmp_path / "solution.py").write_text(code)

            # write tests if provided
            if tests:
                (tmp_path / "test_solution.py").write_text(tests)

            cmd = [
                "docker", "run", "--rm",
                "-v", f"{tmp_path}:/workspace",
                "-w", "/workspace",
                self.IMAGE,
                "bash", "-c",
                self._build_command(tests)
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                return {
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "returncode": proc.returncode,
                    "timeout": False
                }

            except subprocess.TimeoutExpired:
                return {
                    "stdout": "",
                    "stderr": "TIMEOUT",
                    "returncode": -1,
                    "timeout": True
                }

    def _build_command(self, tests: str | None) -> str:
        if tests:
            return "pytest -q"
        return "python solution.py"