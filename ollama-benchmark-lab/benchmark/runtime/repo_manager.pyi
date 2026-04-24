from pathlib import Path

class RepoManager:
    def get_repo(self, repo_url: str, commit: str) -> Path: ...
