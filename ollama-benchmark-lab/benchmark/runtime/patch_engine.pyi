from pathlib import Path

class PatchEngine:
    def apply(self, repo_path: Path, patch: str): ...
