import subprocess
from pathlib import Path
import shutil

from benchmark.repos.cache import RepoCache

CACHE_DIR = Path(".cache/repos")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class RepoManager:
    """
    Clones repos once, then uses snapshot cache per commit.
    """

    def __init__(self):
        self.repo_cache = RepoCache()

    def _repo_name(self, repo_url: str) -> str:
        return repo_url.split("/")[-1].replace(".git", "")

    def _repo_path(self, repo_url: str) -> Path:
        return CACHE_DIR / self._repo_name(repo_url)

    def ensure_cloned(self, repo_url: str) -> Path:
        repo_path = self._repo_path(repo_url)

        if not repo_path.exists():
            print(f"[RepoManager] cloning {repo_url}")
            subprocess.run(
                ["git", "clone", repo_url, str(repo_path)],
                check=True
            )

        return repo_path

    def checkout(self, repo_path: Path, commit: str):
        """
        Checkout commit in base repo (used only for snapshot creation).
        """
        subprocess.run(
            ["git", "fetch", "--all"],
            cwd=repo_path,
            check=True
        )

        subprocess.run(
            ["git", "checkout", commit],
            cwd=repo_path,
            check=True
        )

    def get_repo(self, repo_url: str, commit: str) -> Path:
        """
        Returns a snapshot-safe repo path for execution.
        """
        base_repo = self.ensure_cloned(repo_url)

        snapshot_path = self.repo_cache.snapshot_path(repo_url, commit)

        if snapshot_path.exists():
            print(f"[RepoManager] using cached snapshot {snapshot_path}")
            return snapshot_path

        print(f"[RepoManager] creating snapshot for {commit}")

        # checkout base repo to correct commit
        self.checkout(base_repo, commit)

        # create snapshot
        shutil.copytree(base_repo, snapshot_path)

        return snapshot_path