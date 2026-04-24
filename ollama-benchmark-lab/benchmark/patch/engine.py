import subprocess
from pathlib import Path
import tempfile


class PatchEngine:
    """
    Applies diff patches to a repository safely.
    """

    def apply_patch(self, repo_path: Path, patch_text: str):
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmp:
            tmp.write(patch_text)
            patch_file = tmp.name

        try:
            result = subprocess.run(
                ["git", "apply", patch_file],
                cwd=repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }

            return {"success": True}

        finally:
            Path(patch_file).unlink(missing_ok=True)