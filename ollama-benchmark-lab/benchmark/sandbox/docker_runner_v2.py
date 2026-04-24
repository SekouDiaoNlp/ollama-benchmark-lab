import os
import subprocess
from pathlib import Path
import tempfile

from benchmark.patch.engine import PatchEngine


class DockerRunnerV2:
    """
    Sandbox runner for SWE-bench tasks.
    """

    def __init__(self, patch_engine=None):
        # FIX: allow zero-arg construction (prevents crash)
        self.patch_engine = patch_engine or PatchEngine()

    def run(self, task):
        repo_url = task.get("repo_url")

        if not repo_url:
            raise RuntimeError("Task missing repo_url")

        repo_path = task.get("snapshot_path")

        if repo_path:
            repo_path = Path(repo_path)
        else:
            repo_path = self._clone_repo(repo_url)

        patch_text = task.get("patch") or ""

        repo_path = self.patch_engine.apply_patch(repo_path, patch_text)

        return {"repo_path": str(repo_path)}

    # --------------------------------------------------
    # SAFE NON-INTERACTIVE CLONE (FIX FOR YOUR ISSUE)
    # --------------------------------------------------

    def _clone_repo(self, repo_url: str) -> Path:
        tmp_dir = Path(tempfile.mkdtemp(prefix="swebench_"))

        env = os.environ.copy()

        # FORCE NON-INTERACTIVE MODE
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GCM_INTERACTIVE"] = "never"
        env["GIT_ASKPASS"] = "echo"

        cmd = [
            "git",
            "clone",
            "--depth",
            "1",
            repo_url,
            str(tmp_dir),
        ]

        proc = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
        )

        if proc.returncode != 0:
            raise RuntimeError(
                "Git clone failed (non-interactive mode enforced)\n\n"
                f"STDERR:\n{proc.stderr.strip()}\n\n"
                "Hint: ensure repo_url is public or cached locally."
            )

        return tmp_dir