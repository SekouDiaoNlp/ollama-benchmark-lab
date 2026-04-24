import subprocess
from pathlib import Path


class RepoManager:
    """
    Handles cloning and caching repositories per task.
    """

    def __init__(self, cache_dir="repo_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _repo_path(self, repo_url: str):
        name = repo_url.split("/")[-1].replace(".git", "")
        return self.cache_dir / name

    def ensure_repo(self, repo_url: str):
        path = self._repo_path(repo_url)

        if not path.exists():
            subprocess.run(
                ["git", "clone", repo_url, str(path)],
                check=True
            )

        return path

    def checkout(self, repo_path: Path, commit: str):
        subprocess.run(
            ["git", "fetch"],
            cwd=repo_path,
            check=True
        )

        subprocess.run(
            ["git", "checkout", commit],
            cwd=repo_path,
            check=True
        )

        return repo_path