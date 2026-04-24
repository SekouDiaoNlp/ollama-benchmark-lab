from pathlib import Path

class PatchEngine:
    def apply_patch(self, repo_path: Path, patch_text: str) -> Path: ...
