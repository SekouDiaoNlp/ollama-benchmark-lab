from pathlib import Path
import shutil


class RepoManager:
    def __init__(self, repo_cache):
        self.repo_cache = repo_cache

    def get_repo(self, repo_url: str, commit: str) -> Path:
        """
        Returns a SNAPSHOT PATH (always Path object).
        """

        snapshot_path = self.repo_cache.snapshot_path(repo_url, commit)

        # 🔥 FIX: normalize type immediately
        snapshot_path = Path(snapshot_path)

        if snapshot_path.exists():
            print(f"[RepoManager] using cached snapshot {snapshot_path}")
            return snapshot_path

        print(f"[RepoManager] creating snapshot for {commit}")

        base_repo = self._checkout_repo(repo_url, commit)

        snapshot_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copytree(base_repo, snapshot_path)

        return snapshot_path

    def _checkout_repo(self, repo_url: str, commit: str) -> Path:
        """
        Placeholder: assumes local checkout exists.
        """
        # In real system this would clone repo
        return Path(f"/tmp/repos/{commit}")