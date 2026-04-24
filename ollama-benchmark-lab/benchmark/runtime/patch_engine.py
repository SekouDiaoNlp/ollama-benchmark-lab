import subprocess
from pathlib import Path


class PatchEngine:
    """
    Applies patch/diff inside repo.
    """

    def apply_patch(self, repo_path: Path, patch_text: str):
        patch_file = repo_path / "temp.patch"
        patch_file.write_text(patch_text)

        subprocess.run(
            ["git", "apply", str(patch_file)],
            cwd=repo_path,
            check=True
        )

        patch_file.unlink()