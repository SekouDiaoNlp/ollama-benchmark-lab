import subprocess
import shutil
import tempfile
from pathlib import Path

from benchmark.repos.manager import RepoManager
from benchmark.patch.engine import PatchEngine


class DockerRunner:
    """
    Full SWE-bench parity runner.
    """

    IMAGE = "python:3.12-slim"

    def __init__(self):
        self.repo_manager = RepoManager()
        self.patch_engine = PatchEngine()

    def run(self, task: dict):
        """
        Executes full SWE-bench flow:
        clone → checkout → patch → test
        """

        repo_url = task.get("repo")
        commit = task.get("base_commit")
        patch = task.get("patch", "")

        workdir = tempfile.mkdtemp(prefix="swe_repo_")

        try:
            # --------------------------------------------------
            # 1. Clone + checkout
            # --------------------------------------------------
            repo_path = self.repo_manager.ensure_repo(repo_url)

            working_copy = Path(workdir) / "repo"
            shutil.copytree(repo_path, working_copy)

            self.repo_manager.checkout(working_copy, commit)

            # --------------------------------------------------
            # 2. Apply patch
            # --------------------------------------------------
            if patch:
                patch_result = self.patch_engine.apply_patch(
                    working_copy,
                    patch
                )

                if not patch_result["success"]:
                    return {
                        "task_id": task.get("id"),
                        "passed": False,
                        "error": patch_result["error"],
                        "stage": "patch"
                    }

            # --------------------------------------------------
            # 3. Run inside Docker
            # --------------------------------------------------
            entrypoint = task.get("execution", {}).get(
                "entrypoint",
                "pytest -q"
            )

            cmd = [
                "docker", "run", "--rm",
                "-v", f"{working_copy}:/workspace",
                "-w", "/workspace",
                self.IMAGE,
                "bash", "-lc",
                f"pip install -q -e . || true && {entrypoint}"
            ]

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
                "stage": "execution"
            }

        finally:
            shutil.rmtree(workdir, ignore_errors=True)