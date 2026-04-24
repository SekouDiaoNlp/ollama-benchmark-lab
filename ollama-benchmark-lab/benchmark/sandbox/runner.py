from __future__ import annotations

import subprocess
import tempfile
import textwrap
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SandboxResult:
    passed: bool
    returncode: int
    stdout: str
    stderr: str
    timeout: bool


class SandboxRunner:

    def run_code_with_tests(
        self,
        code: str,
        test_code: str,
        timeout: int = 5
    ) -> SandboxResult:

        with tempfile.TemporaryDirectory() as tmp:

            # Write solution
            solution_path = os.path.join(tmp, "solution.py")
            with open(solution_path, "w") as f:
                f.write(code)

            # Write hidden tests
            test_path = os.path.join(tmp, "test_hidden.py")
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
                    passed=result.returncode == 0,
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    timeout=False
                )

            except subprocess.TimeoutExpired as e:
                return SandboxResult(
                    passed=False,
                    returncode=-1,
                    stdout="",
                    stderr="TIMEOUT",
                    timeout=True
                )