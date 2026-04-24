import os
import subprocess
from pathlib import Path

CACHE = Path("/tmp/swe_repo_cache")
CACHE.mkdir(exist_ok=True, parents=True)

class RepoManager:

    def get_repo(self, repo_url: str):
        name = repo_url.replace("/", "_").replace(":", "_")
        path = CACHE / name

        if not path.exists():
            subprocess.run([
                "git", "clone", repo_url, str(path)
            ], check=True)

        return path