from __future__ import annotations

from typing import Dict, Any
from benchmark.sandbox.docker_executor import DockerExecutor


class PytestRunner:
    """
    Runs hidden SWE-bench tests using Docker + pytest.
    """

    def __init__(self):
        self.executor = DockerExecutor()

    def evaluate(self, code: str, tests: str) -> Dict[str, Any]:

        result = self.executor.run(
            code=code,
            tests=tests,
            timeout=8
        )

        passed = result["returncode"] == 0 and not result["timeout"]

        return {
            "passed": passed,
            "stdout": result["stdout"],
            "stderr": result["stderr"]
        }