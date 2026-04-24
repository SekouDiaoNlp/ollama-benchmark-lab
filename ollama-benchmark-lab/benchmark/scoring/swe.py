"""
SWE-bench scorer using DockerSandboxRunner.

This module extracts code from outputs and evaluates it against
hidden tests using the Docker sandbox execution runner.
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from benchmark.sandbox.docker_runner import DockerSandboxRunner


class SWEBenchScorer:
    """
    Scores coding tasks by executing them against hidden tests in Docker.
    """

    def __init__(self) -> None:
        """Initialize the DockerSandboxRunner dependency."""
        self.runner: DockerSandboxRunner = DockerSandboxRunner()

    def score(self, task: Dict[str, Any], output: str) -> float:
        """
        Score a task by running extracted code against hidden tests.

        Args:
            task (Dict[str, Any]): The task containing 'hidden_tests'.
            output (str): The raw model output.

        Returns:
            float: The evaluation score.
        """
        code: str = self._extract(output)
        tests: Optional[str] = task.get("hidden_tests")

        if not tests:
            return 0.3

        result: Any = self.runner.run(code, tests)

        if result.timeout:
            return 0.1

        if result.passed:
            return 1.0

        # partial credit
        if "AssertionError" in result.stderr:
            return 0.4

        return 0.2

    def _extract(self, output: str) -> str:
        """
        Extract a python code block from a raw model output.

        Args:
            output (str): The raw output containing code blocks.

        Returns:
            str: The extracted code block.
        """
        if "```" in output:
            for block in output.split("```"):
                if "def " in block or "class " in block:
                    return block.strip()
        return output