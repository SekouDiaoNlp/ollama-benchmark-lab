"""
Patch application engine for SWE-bench execution.

This module provides the PatchEngine class, designed to strictly apply diffs
to a git repository utilizing `git apply` exactly as a CI/CD pipeline would.

Example:
    >>> from pathlib import Path
    >>> engine = PatchEngine()
    >>> engine.apply(Path("/tmp/repo"), "--- a/foo.py\\n+++ b/foo.py\\n...")
"""

import subprocess
from pathlib import Path


class PatchEngine:
    """
    Applies SWE-bench text patches cleanly to repository clones.
    """

    def apply(self, repo_path: Path, patch: str) -> Path:
        """
        Apply a raw text diff to the specified repository.

        This method creates a temporary diff file, applies it using git,
        and subsequently deletes the file to ensure a clean working tree.

        Args:
            repo_path (Path): The working directory of the git repository.
            patch (str): The raw text diff content to apply.

        Returns:
            Path: The repository path, returned for convenience in call chains.

        Raises:
            subprocess.CalledProcessError: If `git apply` fails to apply the patch cleanly.
        """
        patch_file: Path = repo_path / "_patch.diff"
        patch_file.write_text(patch)

        try:
            subprocess.run(
                ["git", "apply", "--whitespace=fix", str(patch_file)],
                cwd=str(repo_path),
                check=True
            )
        finally:
            if patch_file.exists():
                patch_file.unlink()

        return repo_path

    def apply_patch(self, repo_path: Path, patch: str) -> Path:
        """
        Alias for apply() to maintain compatibility with legacy DockerRunner.

        Args:
            repo_path (Path): The working directory of the git repository.
            patch (str): The raw text diff content to apply.

        Returns:
            Path: The repository path.
        """
        return self.apply(repo_path, patch)