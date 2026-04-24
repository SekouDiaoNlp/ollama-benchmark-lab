from __future__ import annotations

from benchmark.sandbox.runner import SandboxRunner
from typing import Dict, Any


class SWEHarnessScorer:

    def __init__(self):
        self.sandbox = SandboxRunner()

    def score(self, task: Dict[str, Any], output: str) -> float:

        code = self._extract_code(output)

        test_code = task.get("hidden_tests")

        if not test_code:
            return 0.3  # fallback if missing tests

        result = self.sandbox.run_code_with_tests(code, test_code)

        if result.timeout:
            return 0.1

        if result.passed:
            return 1.0

        # partial credit heuristic
        if "AssertionError" in result.stderr:
            return 0.4

        return 0.2

    def _extract_code(self, output: str) -> str:
        if "```" in output:
            parts = output.split("```")
            for p in parts:
                if "def " in p or "class " in p:
                    return p.strip()
        return output