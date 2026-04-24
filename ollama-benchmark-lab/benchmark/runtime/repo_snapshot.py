import subprocess
from pathlib import Path
import shutil
import hashlib

CACHE = Path(".cache/swe_repos")
CACHE.mkdir(parents=True, exist_ok=True)


class RepoSnapshot:
    """
    Ensures deterministic repo state per task.
    """

    def get(self, repo_url: str, commit: str) -> Path:
        repo_hash = hashlib.md5(f"{repo_url}@{commit}".encode()).hexdigest()
        target = CACHE / repo_hash

        if target.exists():
            return target

        subprocess.run(["git", "clone", repo_url, str(target)], check=True)
        subprocess.run(["git", "checkout", commit], cwd=target, check=True)

        return target