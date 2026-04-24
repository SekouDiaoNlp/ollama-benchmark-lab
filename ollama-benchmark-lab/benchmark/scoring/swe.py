from __future__ import annotations

from benchmark.sandbox.docker_runner import DockerSandboxRunner
from typing import Dict, Any


class SWEBenchScorer:

    def __init__(self):
        self.runner = DockerSandboxRunner()

    def score(self, task: Dict[str, Any], output: str) -> float:

        code = self._extract(output)
        tests = task.get("hidden_tests")

        if not tests:
            return 0.3

        result = self.runner.run(code, tests)

        if result.timeout:
            return 0.1

        if result.passed:
            return 1.0

        # partial credit
        if "AssertionError" in result.stderr:
            return 0.4

        return 0.2

    def _extract(self, output: str) -> str:
        if "```" in output:
            for block in output.split("```"):
                if "def " in block or "class " in block:
                    return block.strip()
        return output