import subprocess
from pathlib import Path
import tempfile
import shutil


class PatchEngine:
    """
    Applies model-generated patches to a repo snapshot
    before execution.
    """

    def __init__(self):
        pass

    def apply_patch(self, repo_path: Path, patch_text: str) -> Path:
        """
        Applies a unified diff patch to a repo snapshot.

        Returns a new patched workspace (isolated copy).
        """

        working_dir = Path(tempfile.mkdtemp(prefix="patched_repo_"))

        shutil.copytree(repo_path, working_dir, dirs_exist_ok=True)

        patch_file = working_dir / "patch.diff"
        patch_file.write_text(patch_text)

        result = subprocess.run(
            ["git", "apply", str(patch_file)],
            cwd=working_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Patch failed:\n{result.stderr}\n{result.stdout}"
            )

        return working_dir