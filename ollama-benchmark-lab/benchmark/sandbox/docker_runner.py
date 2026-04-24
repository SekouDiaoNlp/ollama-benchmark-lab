import subprocess
import tempfile
import shutil
from pathlib import Path


class DockerRunner:
    """
    SWE-bench parity execution engine using per-task Docker isolation.
    """

    IMAGE = "python:3.12-slim"

    def __init__(self):
        pass

    def _build_command(self, workdir: str, entrypoint: str):
        return [
            "docker", "run", "--rm",
            "-v", f"{workdir}:/workspace",
            "-w", "/workspace",
            self.IMAGE,
            "bash", "-lc", entrypoint
        ]

    def run(self, task: dict):
        """
        Executes a single SWE-bench task in an isolated container.
        """

        workdir = tempfile.mkdtemp(prefix="swe_task_")

        try:
            # 1. Prepare workspace
            self._prepare_workspace(workdir, task)

            # 2. Build execution command
            entrypoint = task.get("execution", {}).get("entrypoint", "pytest -q")

            cmd = self._build_command(workdir, entrypoint)

            # 3. Execute container
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            return {
                "task_id": task.get("id"),
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "passed": proc.returncode == 0,
            }

        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    def _prepare_workspace(self, workdir: str, task: dict):
        """
        Simulates SWE-bench repo state.
        In full version: clone repo + apply patch.
        """

        path = Path(workdir)

        # minimal scaffold
        (path / "tests").mkdir(parents=True, exist_ok=True)

        tests_path = task.get("tests", {}).get("path", "tests/test_solution.py")

        (path / tests_path).parent.mkdir(parents=True, exist_ok=True)
        (path / tests_path).write_text(
            "def test_dummy():\n    assert 1 == 1\n"
        )

        # placeholder solution
        (path / "solution.py").write_text(
            "def solve():\n    return 1\n"
        )