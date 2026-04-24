"""
Codebase context extraction utilities.

This module provides heuristics for intelligently extracting repository
files to build dense context prompts for local LLMs.

Example:
    >>> from pathlib import Path
    >>> ctx = extract_repo_context(Path("/tmp/repo"), max_files=2)
"""

from pathlib import Path
from typing import List


def extract_repo_context(repo_path: Path, max_files: int = 5) -> str:
    """
    Lightweight heuristic: extract key Python files for the prompt.

    This function attempts to gather up to `max_files` python scripts,
    reading the first 2000 characters of each to prevent blowing out
    the context window of smaller local LLMs.

    Args:
        repo_path (Path): The root directory of the repository.
        max_files (int): The maximum number of files to extract. Defaults to 5.

    Returns:
        str: A concatenated string containing the paths and truncated contents of the files.
    """
    important_files: List[str] = []

    for f in repo_path.rglob("*.py"):
        if len(important_files) >= max_files:
            break

        try:
            content: str = f.read_text()[:2000]
            important_files.append(f"\nFILE: {f}\n{content}\n")
        except Exception:
            continue

    return "\n".join(important_files)