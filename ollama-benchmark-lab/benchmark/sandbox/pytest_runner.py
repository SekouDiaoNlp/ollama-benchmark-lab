"""
Pytest execution utility for isolated test runs.

This module provides the `run_pytest` function which executes test suites
inside an acquired SandboxInstance.

Example:
    >>> pool = SandboxPool(size=1)
    >>> sandbox = pool.acquire()
    >>> res = run_pytest(sandbox, "tests/test_foo.py")
"""

from typing import Any, Dict

from benchmark.sandbox.pool import SandboxInstance


def run_pytest(sandbox: SandboxInstance, task_path: str) -> Dict[str, Any]:
    """
    Execute hidden tests inside a pre-warmed sandbox using pytest.

    Args:
        sandbox (SandboxInstance): The active Docker sandbox container.
        task_path (str): The file path or directory containing the pytest suite.

    Returns:
        Dict[str, Any]: A dictionary containing a 'passed' boolean and 'raw_output' string.
    """
    cmd = [
        "pytest",
        task_path,
        "-q",
        "--disable-warnings",
        "--maxfail=1"
    ]

    result: str = sandbox.exec(cmd, timeout=60)

    passed: bool = "failed" not in result.lower()

    return {
        "passed": passed,
        "raw_output": result
    }