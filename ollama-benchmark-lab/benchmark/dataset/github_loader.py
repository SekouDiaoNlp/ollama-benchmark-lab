"""
GitHub dataset loader for SWE-style tasks.

This module provides the GitHubDatasetLoader class for cloning repositories
and extracting benchmark task definitions from them.
"""

from __future__ import annotations

import subprocess
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Any

class GitHubDatasetLoader:
    """
    Loads SWE-style tasks from GitHub repositories.
    """

    def clone_repo(self, repo_url: str) -> Path:
        """
        Clone a GitHub repository to a temporary directory.

        Args:
            repo_url (str): The URL of the repository to clone.

        Returns:
            Path: The path to the cloned repository.

        Raises:
            subprocess.CalledProcessError: If the git clone command fails.
        """
        tmp = tempfile.mkdtemp()
        path = Path(tmp)

        subprocess.run(
            ["git", "clone", repo_url, str(path)],
            check=True,
            capture_output=True
        )

        return path

    def load_tasks(self, repo_path: Path) -> List[Dict[str, Any]]:
        """
        Scan a repository path for task.json files and load them.

        Args:
            repo_path (Path): The path to the repository.

        Returns:
            List[Dict[str, Any]]: A list of normalized task configurations.
        """
        tasks: List[Dict[str, Any]] = []

        for f in repo_path.glob("**/task.json"):
            try:
                data: Dict[str, Any] = json.loads(f.read_text())

                tasks.append({
                    "id": data.get("id", f.stem),
                    "mode": data.get("mode", "SWE"),
                    "public_prompt": data.get("prompt", ""),
                    "tests": data.get("tests"),
                    "rubric": data.get("rubric", {"correctness": 1.0}),
                    "version": "github-import"
                })

            except Exception:
                # Silently skip malformed task files
                continue

        return tasks

    def load_from_github(self, repo_url: str) -> List[Dict[str, Any]]:
        """
        Clone a repository and load its tasks in one step.

        Args:
            repo_url (str): The URL of the repository.

        Returns:
            List[Dict[str, Any]]: A list of task configurations.
        """
        repo = self.clone_repo(repo_url)
        return self.load_tasks(repo)