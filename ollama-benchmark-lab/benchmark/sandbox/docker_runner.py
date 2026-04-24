from __future__ import annotations

import subprocess
import tempfile
import os
from dataclasses import dataclass


@dataclass
class DockerResult:
    passed: bool
    stdout: str
    stderr: str
    timeout: bool


class DockerSandboxRunner:

    IMAGE = "python:3.12-slim"

    def run(self, code: str, tests: str, timeout: int = 10) -> DockerResult:

        with tempfile.TemporaryDirectory() as tmp:

            # write solution
            with open(f"{tmp}/solution.py", "w") as f:
                f.write(code)

            # write tests
            with open(f"{tmp}/test_hidden.py", "w") as f:
                f.write(tests)

            try:
                cmd = [
                    "docker", "run", "--rm",
                    "-v", f"{tmp}:/workspace",
                    "-w", "/workspace",
                    "--network", "none",
                    self.IMAGE,
                    "bash", "-c",
                    "pip install pytest -q && pytest -q"
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                return DockerResult(
                    passed=result.returncode == 0,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    timeout=False
                )

            except subprocess.TimeoutExpired:
                return DockerResult(
                    passed=False,
                    stdout="",
                    stderr="TIMEOUT",
                    timeout=True
                )