import shutil
from pathlib import Path


class RepoCache:
    """
    Stores repo snapshots per commit to avoid repeated checkout/copy.
    """

    def __init__(self, base_dir=".cache/repo_snapshots"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _repo_name(self, repo_url: str) -> str:
        return repo_url.split("/")[-1].replace(".git", "")

    def snapshot_path(self, repo_url: str, commit: str) -> Path:
        repo_name = self._repo_name(repo_url)
        return self.base_dir / f"{repo_name}_{commit}"

    def get_or_create(self, repo_path: Path, repo_url: str, commit: str) -> Path:
        """
        Optional helper if you want unified interface later.
        """
        snap = self.snapshot_path(repo_url, commit)

        if snap.exists():
            return snap

        shutil.copytree(repo_path, snap)
        return snap