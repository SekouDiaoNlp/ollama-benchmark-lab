from _typeshed import Incomplete
from pathlib import Path

logger: Incomplete

class RepoSnapshot:
    def __init__(self) -> None: ...
    def get(self, repo_url: str, commit: str) -> Path: ...
