import shutil
from pathlib import Path

from benchmark.runtime.repo_manager import RepoManager
from benchmark.sandbox.image_builder import ImageBuilder


class DockerRunner:

    def __init__(self):
        self.repo_manager = RepoManager()
        self.image_builder = ImageBuilder()

    def run(self, repo_path: str, command: str):

        # -----------------------------
        # TRACE INPUTS (CRITICAL)
        # -----------------------------
        print("[DOCKER DEBUG] repo_path type:", type(repo_path))
        print("[DOCKER DEBUG] repo_path value:", repo_path)
        print("[DOCKER DEBUG] command type:", type(command))
        print("[DOCKER DEBUG] command value:", command)

        snapshot_path = self.repo_manager.get_repo(repo_path, "HEAD")

        # -----------------------------
        # TRACE SNAPSHOT OUTPUT
        # -----------------------------
        print("[DOCKER DEBUG] snapshot_path BEFORE conversion:", type(snapshot_path), snapshot_path)

        # HARDEN TYPE SAFETY
        if snapshot_path is not None:
            snapshot_path = Path(snapshot_path)

        print("[DOCKER DEBUG] snapshot_path AFTER Path():", type(snapshot_path), snapshot_path)

        if snapshot_path is None or not snapshot_path.exists():
            raise RuntimeError(
                f"[DOCKER RUNNER] Missing snapshot or invalid path: {snapshot_path}"
            )

        # -----------------------------
        # WORKING COPY SETUP
        # -----------------------------
        working_copy = Path(f"/tmp/workspace/{hash(str(snapshot_path))}")

        print("[DOCKER DEBUG] working_copy BEFORE exists check:", type(working_copy), working_copy)

        if working_copy.exists():
            shutil.rmtree(working_copy)

        shutil.copytree(snapshot_path, working_copy)

        print("[DOCKER DEBUG] working_copy AFTER setup:", type(working_copy), working_copy)

        image = self.image_builder.build(snapshot_path)

        return self._execute_container(image, working_copy, command)

    def _execute_container(self, image: str, working_copy: Path, command: str):

        import subprocess

        print("[DOCKER DEBUG] EXECUTE container:")
        print("  image:", image)
        print("  working_copy:", working_copy)
        print("  command:", command)

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{working_copy}:/workspace",
            image,
            "bash", "-lc", command
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        print("[DOCKER DEBUG] returncode:", result.returncode)
        print("[DOCKER DEBUG] stdout:", result.stdout[:500])
        print("[DOCKER DEBUG] stderr:", result.stderr[:500])

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }