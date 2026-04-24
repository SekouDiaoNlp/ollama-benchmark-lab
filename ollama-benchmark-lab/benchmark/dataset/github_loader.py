from __future__ import annotations

import subprocess
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Any


class GitHubDatasetLoader:
    """
    Loads SWE-style tasks from GitHub repos.
    Supports:
    - cloning repo
    - extracting tasks
    - mapping to benchmark format
    """

    def clone_repo(self, repo_url: str) -> Path:

        tmp = tempfile.mkdtemp()
        path = Path(tmp)

        subprocess.run(
            ["git", "clone", repo_url, str(path)],
            check=True,
            capture_output=True
        )

        return path


    def load_tasks(self, repo_path: Path) -> List[Dict[str, Any]]:

        tasks = []

        for f in repo_path.glob("**/task.json"):
            try:
                data = json.loads(f.read_text())

                tasks.append({
                    "id": data.get("id", f.stem),
                    "mode": data.get("mode", "SWE"),
                    "public_prompt": data.get("prompt", ""),
                    "tests": data.get("tests"),
                    "rubric": data.get("rubric", {"correctness": 1.0}),
                    "version": "github-import"
                })

            except Exception:
                continue

        return tasks


    def load_from_github(self, repo_url: str) -> List[Dict[str, Any]]:

        repo = self.clone_repo(repo_url)
        return self.load_tasks(repo)