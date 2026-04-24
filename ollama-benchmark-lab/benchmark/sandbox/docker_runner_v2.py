import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class DockerRunnerV2:
    """
    Production-grade SWE-bench execution engine.

    Features:
    - snapshot-based repo caching
    - docker image reuse per repo+commit
    - per-task isolated containers
    - deterministic execution
    """

    def __init__(self, cache_dir=".cache/docker"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------

    def run(self, task: dict) -> dict:
        task_id = task.get("task_id", "unknown")

        repo_path = self._prepare_snapshot(task)
        image = self._get_or_build_image(task, repo_path)

        result = self._run_container(task, image)

        return {
            "task_id": task_id,
            "passed": result["passed"],
            "logs": result["logs"],
            "image": image,
        }

    # -----------------------------------------------------
    # SNAPSHOT LAYER
    # -----------------------------------------------------

    def _prepare_snapshot(self, task: dict) -> Path:
        repo_url = task["repo_url"]
        commit = task["commit"]

        repo = task.get("repo", "repo")
        key = self._hash(f"{repo}@{commit}")

        snapshot_dir = self.cache_dir / "snapshots" / key

        if snapshot_dir.exists():
            return snapshot_dir

        snapshot_dir.mkdir(parents=True, exist_ok=True)

        tmp = tempfile.mkdtemp()

        subprocess.run(["git", "clone", repo_url, tmp], check=True)
        subprocess.run(["git", "checkout", commit], cwd=tmp, check=True)

        shutil.copytree(tmp, snapshot_dir, dirs_exist_ok=True)
        shutil.rmtree(tmp)

        return snapshot_dir

    # -----------------------------------------------------
    # IMAGE LAYER (CACHE)
    # -----------------------------------------------------

    def _get_or_build_image(self, task: dict, snapshot: Path) -> str:
        """
        Builds or reuses docker image for repo snapshot.
        """

        repo = task.get("repo", "unknown")
        commit = task.get("commit", "HEAD")

        image_tag = f"swebench:{self._hash(repo + commit)}"

        result = subprocess.run(
            ["docker", "images", "-q", image_tag],
            capture_output=True,
            text=True,
        )

        if result.stdout.strip():
            return image_tag

        dockerfile = self._generate_dockerfile(snapshot)

        build_dir = tempfile.mkdtemp()
        shutil.copytree(snapshot, build_dir, dirs_exist_ok=True)

        Path(build_dir, "Dockerfile").write_text(dockerfile)

        subprocess.run(
            ["docker", "build", "-t", image_tag, build_dir],
            check=True,
        )

        shutil.rmtree(build_dir)

        return image_tag

    # -----------------------------------------------------
    # EXECUTION LAYER
    # -----------------------------------------------------

    def _run_container(self, task: dict, image: str) -> dict:
        """
        Runs task inside isolated container.
        """

        cmd = task.get("execution", {}).get("entrypoint", "pytest -q")

        container_cmd = [
            "docker",
            "run",
            "--rm",
            "-i",
            image,
            "/bin/bash",
            "-lc",
            cmd,
        ]

        proc = subprocess.run(
            container_cmd,
            capture_output=True,
            text=True,
        )

        output = proc.stdout + proc.stderr

        passed = proc.returncode == 0

        return {
            "passed": passed,
            "logs": output[-4000:],  # truncate logs
        }

    # -----------------------------------------------------
    # UTIL
    # -----------------------------------------------------

    def _generate_dockerfile(self, snapshot: Path) -> str:
        return """
FROM python:3.12-slim

WORKDIR /workspace

COPY . /workspace

RUN pip install -U pip
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
"""

    def _hash(self, s: str) -> str:
        return hashlib.sha256(s.encode()).hexdigest()[:16]