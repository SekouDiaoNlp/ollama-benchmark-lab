import tempfile
from pathlib import Path


def run_pytest(sandbox, task_path: str):
    """
    Executes hidden tests inside sandbox.
    """

    cmd = [
        "pytest",
        task_path,
        "-q",
        "--disable-warnings",
        "--maxfail=1"
    ]

    result = sandbox.exec(cmd, timeout=60)

    passed = "failed" not in result.lower()

    return {
        "passed": passed,
        "raw_output": result
    }