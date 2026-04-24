from __future__ import annotations

import subprocess
import uuid
import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Sandbox:
    id: str
    container_name: str


class SandboxPool:
    """
    Persistent Docker sandbox pool.

    Keeps warm Python containers alive and reuses them
    to avoid per-task container startup overhead.
    """

    def __init__(self, size: int = 4):
        self.size = size
        self.pool: list[Sandbox] = []
        self.available: list[Sandbox] = []

    # -----------------------------------------------------
    # INIT POOL
    # -----------------------------------------------------

    def start(self):
        for _ in range(self.size):
            sandbox = self._create_container()
            self.pool.append(sandbox)
            self.available.append(sandbox)

    def _create_container(self) -> Sandbox:
        name = f"sandbox_{uuid.uuid4().hex[:8]}"

        cmd = [
            "docker", "run", "-d",
            "--rm",
            "--name", name,
            "python:3.11-slim",
            "sleep", "infinity"
        ]

        subprocess.check_call(cmd)

        return Sandbox(id=name, container_name=name)

    # -----------------------------------------------------
    # ACQUIRE / RELEASE
    # -----------------------------------------------------

    def acquire(self) -> Sandbox:
        while not self.available:
            time.sleep(0.05)

        return self.available.pop()

    def release(self, sandbox: Sandbox):
        self.available.append(sandbox)

    # -----------------------------------------------------
    # EXECUTION
    # -----------------------------------------------------

    def run(self, sandbox: Sandbox, code: str, test_cmd: str, timeout: int = 60) -> dict:
        """
        Executes code inside persistent container.
        """

        workdir = f"/tmp/run_{uuid.uuid4().hex}"

        try:
            # 1. create working directory
            subprocess.check_call([
                "docker", "exec", sandbox.container_name,
                "mkdir", "-p", workdir
            ])

            # 2. write code
            self._write_file(sandbox, f"{workdir}/solution.py", code)

            # 3. run tests
            result = subprocess.run(
                [
                    "docker", "exec",
                    sandbox.container_name,
                    "bash", "-c",
                    f"cd {workdir} && pip install pytest -q && {test_cmd}"
                ],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": True,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "timeout"
            }

    def _write_file(self, sandbox: Sandbox, path: str, content: str):
        proc = subprocess.Popen(
            ["docker", "exec", "-i", sandbox.container_name, "tee", path],
            stdin=subprocess.PIPE,
            text=True
        )
        proc.communicate(content)

    # -----------------------------------------------------
    # CLEANUP
    # -----------------------------------------------------

    def stop(self):
        for s in self.pool:
            subprocess.call(["docker", "stop", s.container_name])