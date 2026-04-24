from _typeshed import Incomplete
from pathlib import Path

class RepoManager:
    repo_cache: Incomplete
    def __init__(self, repo_cache) -> None: ...
    def get_repo(self, repo_url: str, commit: str) -> Path: ...
