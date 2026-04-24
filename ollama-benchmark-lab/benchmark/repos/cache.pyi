from _typeshed import Incomplete
from pathlib import Path

class RepoCache:
    base_dir: Incomplete
    def __init__(self, base_dir: str = '.cache/repo_snapshots') -> None: ...
    def snapshot_path(self, repo_url: str, commit: str) -> Path: ...
