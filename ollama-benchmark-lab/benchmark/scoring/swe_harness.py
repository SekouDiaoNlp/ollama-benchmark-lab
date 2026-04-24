"""
SWE Harness Scorer using the local SandboxRunner.

This module evaluates code by creating temporary files and executing them
via pytest using the SandboxRunner environment.
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from benchmark.sandbox.runner import SandboxRunner


class SWEHarnessScorer:
    """
    Scores coding tasks by executing them via the local SandboxRunner.
    """

    def __init__(self) -> None:
        """Initialize the SandboxRunner dependency."""
        self.sandbox: SandboxRunner = SandboxRunner()

    def score(self, task: Dict[str, Any], output: str) -> float:
        """
        Score a task by running extracted code against hidden tests.

        Args:
            task (Dict[str, Any]): The task containing 'hidden_tests'.
            output (str): The raw model output.

        Returns:
            float: The evaluation score.
        """
        code: str = self._extract_code(output)

        test_code: Optional[str] = task.get("hidden_tests")

        if not test_code:
            return 0.3  # fallback if missing tests

        result: Any = self.sandbox.run_code_with_tests(code, test_code)

        if result.timeout:
            return 0.1

        if result.passed:
            return 1.0

        # partial credit heuristic
        if "AssertionError" in result.stderr:
            return 0.4

        return 0.2

    def _extract_code(self, output: str) -> str:
        """
        Extract a python code block from a raw model output.

        Args:
            output (str): The raw output containing code blocks.

        Returns:
            str: The extracted code block.
        """
        if "```" in output:
            parts = output.split("```")
            for p in parts:
                if "def " in p or "class " in p:
                    return p.strip()
        return output