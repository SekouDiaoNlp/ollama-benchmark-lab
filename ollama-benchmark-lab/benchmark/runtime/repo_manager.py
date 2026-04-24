import os
import subprocess
from pathlib import Path
import shutil

CACHE_DIR = Path(".cache/repos")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class RepoManager:
    """
    Clones and caches repos for SWE-bench tasks.
    """

    def get_repo(self, repo_url: str, commit: str) -> Path:
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = CACHE_DIR / repo_name

        if not repo_path.exists():
            print(f"[RepoManager] cloning {repo_url}")
            subprocess.run(["git", "clone", repo_url, str(repo_path)], check=True)

        print(f"[RepoManager] resetting to {commit}")
        subprocess.run(["git", "checkout", commit], cwd=repo_path, check=True)

        return repo_path