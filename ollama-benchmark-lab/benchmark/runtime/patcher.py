"""
Legacy patch application utility.

This module provides a standalone `apply_patch` function. For new code,
prefer using the `PatchEngine` class in `benchmark.runtime.patch_engine`.

Example:
    >>> from pathlib import Path
    >>> apply_patch(Path("/tmp/repo"), "--- a/foo\n+++ b/foo")
"""

import subprocess
from pathlib import Path
from typing import Union


def apply_patch(repo_path: Union[str, Path], patch_text: str) -> None:
    """
    Applies a unified diff patch to a git repository using stdin.

    Args:
        repo_path (Union[str, Path]): The path to the repository working directory.
        patch_text (str): The raw patch content.

    Raises:
        RuntimeError: If the patch fails to apply cleanly.
    """
    proc = subprocess.run(
        ["git", "apply"],
        input=patch_text,
        text=True,
        cwd=str(repo_path),
        capture_output=True
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"Patch failed:\n{proc.stderr}"
        )