from pathlib import Path


class RepoCache:
    def __init__(self, base_dir=".cache/repo_snapshots"):
        self.base_dir = Path(base_dir)

    def snapshot_path(self, repo_url: str, commit: str) -> Path:
        snap = self.base_dir / repo_url.replace("/", "_") / commit

        # 🔥 FIX: ALWAYS return Path
        return Path(snap)