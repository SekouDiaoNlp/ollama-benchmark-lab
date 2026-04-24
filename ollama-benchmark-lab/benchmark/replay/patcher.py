"""
Git patch application utility.

This module provides functionality for applying text patches to a 
git repository.
"""

import subprocess
from pathlib import Path
from typing import Union

def apply_patch(repo_path: Union[str, Path], patch_text: str) -> None:
    """
    Apply a git patch to the specified repository path.

    Args:
        repo_path (Union[str, Path]): Path to the repository.
        patch_text (str): Raw text of the patch to apply.

    Raises:
        RuntimeError: If the patch fails to apply cleanly.
    """
    if not patch_text:
        return

    process = subprocess.Popen(
        ["git", "apply"],
        cwd=str(repo_path),
        stdin=subprocess.PIPE,
        text=True
    )
    process.communicate(patch_text)

    if process.returncode != 0:
        raise RuntimeError("Patch failed to apply")