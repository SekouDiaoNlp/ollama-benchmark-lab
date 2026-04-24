import subprocess
from pathlib import Path


class PatchEngine:
    """
    Applies SWE-bench patches exactly as CI would.
    """

    def apply(self, repo_path: Path, patch: str):
        patch_file = repo_path / "_patch.diff"
        patch_file.write_text(patch)

        try:
            subprocess.run(
                ["git", "apply", "--whitespace=fix", str(patch_file)],
                cwd=repo_path,
                check=True
            )
        finally:
            patch_file.unlink()