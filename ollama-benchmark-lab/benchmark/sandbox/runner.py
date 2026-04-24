"""
Local sandbox runner for evaluating individual Python code snippets.

This module provides the SandboxRunner class, which executes generated Python code
alongside isolated hidden tests using a local temporary directory and Pytest.

Example:
    >>> runner = SandboxRunner()
    >>> res = runner.run_code_with_tests("def add(a, b): return a + b", "def test_add(): assert add(1, 2) == 3")
    >>> print(res.passed)
    True
"""

from __future__ import annotations

import subprocess
import tempfile
import os
from dataclasses import dataclass


@dataclass
class SandboxResult:
    """
    Data structure representing the outcome of a local sandbox execution.

    Attributes:
        passed (bool): True if all tests passed successfully.
        returncode (int): The exit code of the Pytest subprocess.
        stdout (str): The standard output from Pytest.
        stderr (str): The standard error from Pytest.
        timeout (bool): True if the execution was aborted due to a timeout limit.
    """
    passed: bool
    returncode: int
    stdout: str
    stderr: str
    timeout: bool


class SandboxRunner:
    """
    A lightweight, local test runner for Python code snippets.
    """

    def run_code_with_tests(
        self,
        code: str,
        test_code: str,
        timeout: int = 5
    ) -> SandboxResult:
        """
        Write code and test files to a temporary directory and execute Pytest.

        Args:
            code (str): The raw Python code (the solution) to evaluate.
            test_code (str): The Pytest-compatible test cases.
            timeout (int): Maximum execution time in seconds. Defaults to 5.

        Returns:
            SandboxResult: The result containing the execution status and output.
        """

        with tempfile.TemporaryDirectory() as tmp:

            # Write solution
            solution_path: str = os.path.join(tmp, "solution.py")
            with open(solution_path, "w") as f:
                f.write(code)

            # Write hidden tests
            test_path: str = os.path.join(tmp, "test_hidden.py")
            with open(test_path, "w") as f:
                f.write(test_code)

            try:
                result = subprocess.run(
                    ["python", "-m", "pytest", "-q", test_path],
                    cwd=tmp,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                return SandboxResult(
                    passed=(result.returncode == 0),
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    timeout=False
                )

            except subprocess.TimeoutExpired:
                return SandboxResult(
                    passed=False,
                    returncode=-1,
                    stdout="",
                    stderr="TIMEOUT",
                    timeout=True
                )