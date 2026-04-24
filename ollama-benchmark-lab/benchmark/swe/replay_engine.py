from __future__ import annotations

import subprocess
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional


# =========================================================
# RESULT
# =========================================================

@dataclass
class ReplayResult:
    success: bool
    score: float
    stdout: str
    stderr: str


# =========================================================
# GITHUB REPLAY ENGINE
# =========================================================

class GitHubReplayEngine:
    """
    True SWE-bench style:
    repo clone → checkout → patch → test
    """

    def __init__(self, cache_dir: str = ".repo_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    # -----------------------------------------------------
    # MAIN ENTRY
    # -----------------------------------------------------

    def run(self, task: Dict[str, Any]) -> ReplayResult:
        repo = task["repo"]["url"]
        commit = task["repo"]["commit"]
        patch = task.get("patch", "")

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)

            repo_path = self._clone_or_restore(repo, workspace)
            self._checkout(repo_path, commit)

            if patch:
                self._apply_patch(repo_path, patch)

            env_ok = self._install_env(repo_path)

            if not env_ok:
                return ReplayResult(
                    success=False,
                    score=0.0,
                    stdout="ENV INSTALL FAILED",
                    stderr=""
                )

            return self._run_tests(repo_path, task)

    # -----------------------------------------------------
    # CLONING (CACHED)
    # -----------------------------------------------------

    def _clone_or_restore(self, repo: str, workspace: Path) -> Path:
        name = repo.split("/")[-1].replace(".git", "")
        cached = self.cache_dir / name

        if cached.exists():
            return shutil.copytree(cached, workspace / name)

        target = workspace / name

        subprocess.run(
            ["git", "clone", repo, str(target)],
            check=True,
            capture_output=True
        )

        shutil.copytree(target, cached, dirs_exist_ok=True)

        return target

    # -----------------------------------------------------
    # CHECKOUT
    # -----------------------------------------------------

    def _checkout(self, repo_path: Path, commit: str):
        subprocess.run(
            ["git", "checkout", commit],
            cwd=repo_path,
            check=True,
            capture_output=True
        )

    # -----------------------------------------------------
    # PATCH APPLY (SWE STYLE)
    # -----------------------------------------------------

    def _apply_patch(self, repo_path: Path, patch: str):
        proc = subprocess.run(
            ["git", "apply", "-"],
            cwd=repo_path,
            input=patch,
            text=True,
            capture_output=True
        )

        if proc.returncode != 0:
            raise RuntimeError(f"PATCH FAILED:\n{proc.stderr}")

    # -----------------------------------------------------
    # ENV INSTALL (SAFE)
    # -----------------------------------------------------

    def _install_env(self, repo_path: Path) -> bool:
        """
        Tries multiple strategies:
        - requirements.txt
        - pyproject.toml
        - setup.py
        """

        try:
            if (repo_path / "requirements.txt").exists():
                subprocess.run(
                    ["pip", "install", "-r", "requirements.txt"],
                    cwd=repo_path,
                    check=True,
                    capture_output=True
                )

            elif (repo_path / "pyproject.toml").exists():
                subprocess.run(
                    ["pip", "install", "."],
                    cwd=repo_path,
                    check=True,
                    capture_output=True
                )

            elif (repo_path / "setup.py").exists():
                subprocess.run(
                    ["pip", "install", "-e", "."],
                    cwd=repo_path,
                    check=True,
                    capture_output=True
                )

            return True

        except subprocess.CalledProcessError:
            return False

    # -----------------------------------------------------
    # TEST RUNNER (PYTEST)
    # -----------------------------------------------------

    def _run_tests(self, repo_path: Path, task: Dict[str, Any]) -> ReplayResult:
        tests_path = task["tests"]["path"]

        proc = subprocess.run(
            ["pytest", tests_path, "-q", "--disable-warnings", "--maxfail=1"],
            cwd=repo_path,
            text=True,
            capture_output=True,
            timeout=30
        )

        success = proc.returncode == 0

        return ReplayResult(
            success=success,
            score=1.0 if success else 0.0,
            stdout=proc.stdout,
            stderr=proc.stderr
        )