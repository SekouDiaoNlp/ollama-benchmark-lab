import subprocess
import tempfile
import shutil
from pathlib import Path

from benchmark.repos.manager import RepoManager
from benchmark.patch.engine import PatchEngine
from benchmark.sandbox.image_builder import ImageBuilder


class DockerRunner:
    """
    SWE-bench parity runner with:
    - repo snapshot reuse
    - Docker image caching
    - patch application
    """

    def __init__(self):
        self.repo_manager = RepoManager()
        self.patch_engine = PatchEngine()
        self.image_builder = ImageBuilder()

    def run(self, task: dict):
        repo_url = task.get("repo")
        commit = task.get("base_commit")
        patch = task.get("patch", "")

        if not repo_url or not commit:
            return {
                "task_id": task.get("id"),
                "passed": False,
                "error": "Missing repo or commit",
                "stage": "setup"
            }

        workdir = tempfile.mkdtemp(prefix="swe_task_")

        try:
            # ==================================================
            # 1. GET SNAPSHOT (IMMUTABLE)
            # ==================================================
            snapshot_path = self.repo_manager.get_repo(repo_url, commit)

            # ==================================================
            # 2. CREATE WORKING COPY (FOR PATCH ONLY)
            # ==================================================
            working_copy = Path(workdir) / "repo"
            shutil.copytree(snapshot_path, working_copy)

            # ==================================================
            # 3. APPLY PATCH (IF ANY)
            # ==================================================
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

            # ==================================================
            # 4. BUILD / GET CACHED IMAGE (FROM SNAPSHOT!)
            # ==================================================
            image = self.image_builder.build(snapshot_path)

            # ==================================================
            # 5. RUN TASK IN DOCKER
            # ==================================================
            entrypoint = task.get("execution", {}).get(
                "entrypoint",
                "pytest -q"
            )

            cmd = [
                "docker", "run", "--rm",
                "-v", f"{working_copy}:/workspace",
                "-w", "/workspace",
                image,
                "bash", "-lc",
                entrypoint
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