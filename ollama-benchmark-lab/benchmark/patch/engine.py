"""
Robust patch application engine for SWE-bench workflows.

This module provides the PatchEngine class, handling structural validation,
safe normalization, and git application with detailed diagnostic outputs.

Example:
    >>> from pathlib import Path
    >>> engine = PatchEngine()
    >>> engine.apply_patch(Path("/repo"), "--- a/foo\n+++ b/foo")
"""

import subprocess
import tempfile
from pathlib import Path
from typing import List


class PatchEngine:
    """
    Robust patch application layer for SWE-bench.

    Handles:
    - structural validation
    - hunk validation
    - safe normalization (NON-DESTRUCTIVE)
    - git apply diagnostics
    """

    def apply_patch(self, repo_path: Path, patch_text: str) -> Path:
        """
        Validates, normalizes, and applies a patch to a local repository.

        Args:
            repo_path (Path): Path to the target git repository.
            patch_text (str): The raw text of the patch to apply.

        Returns:
            Path: The repository path, for chainability.

        Raises:
            RuntimeError: If the patch is invalid or fails to apply.
        """
        if not patch_text or "diff --git" not in patch_text:
            raise RuntimeError("Invalid patch: missing diff header")

        # STEP 1: structural validation
        self._validate_patch_structure(patch_text)

        # STEP 2: hunk validation
        self._validate_patch(patch_text)

        # STEP 3: safe normalization (FIXED)
        patch_text = self._normalize_patch(patch_text)

        # STEP 4: write patch to temp file
        patch_file = tempfile.NamedTemporaryFile(delete=False, suffix=".patch")

        try:
            patch_file.write(patch_text.encode())
            patch_file.close()

            # STEP 5: apply patch
            proc = subprocess.run(
                ["git", "apply", "--whitespace=fix", "--recount", patch_file.name],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
            )

            if proc.returncode != 0:
                raise RuntimeError(self._format_git_error(proc.stderr, patch_text))

        finally:
            Path(patch_file.name).unlink(missing_ok=True)

        return repo_path

    # --------------------------------------------------
    # PATCH NORMALIZATION (SAFE VERSION)
    # --------------------------------------------------

    def _normalize_patch(self, patch: str) -> str:
        """
        ONLY removes known non-diff garbage.
        DOES NOT modify git headers.

        Args:
            patch (str): The raw patch string.

        Returns:
            str: The normalized patch string.
        """
        fixed_lines: List[str] = []

        for line in patch.splitlines():

            # Remove model artifacts only
            if line.startswith("Index:"):
                continue

            # DO NOT touch diff --git lines anymore
            # DO NOT remove a/ b/ prefixes

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    # --------------------------------------------------
    # PATCH VALIDATION
    # --------------------------------------------------

    def _validate_patch_structure(self, patch: str) -> None:
        """
        Validate the diff formatting strictly line-by-line.

        Args:
            patch (str): The patch text.

        Raises:
            RuntimeError: If invalid diff syntax is detected.
        """
        lines: List[str] = patch.splitlines()

        for i, line in enumerate(lines):
            if line.startswith(("diff --git", "@@", "---", "+++")):
                continue

            if line and not (
                line.startswith("+")
                or line.startswith("-")
                or line.startswith(" ")
            ):
                raise RuntimeError(
                    f"Patch corrupted at line {i + 1}: invalid diff syntax -> {line[:80]}"
                )

    def _validate_patch(self, patch_text: str) -> None:
        """
        Ensure the patch contains required hunk headers.

        Args:
            patch_text (str): The patch string.

        Raises:
            RuntimeError: If hunk headers are missing.
        """
        if "@@" not in patch_text:
            raise RuntimeError("Invalid patch: missing hunk headers (@@)")

    # --------------------------------------------------
    # ERROR FORMATTING
    # --------------------------------------------------

    def _format_git_error(self, stderr: str, patch: str) -> str:
        """
        Format a detailed error message from git apply failures.

        Args:
            stderr (str): Standard error output from git.
            patch (str): The patch being applied.

        Returns:
            str: Formatted error diagnostic.
        """
        preview: str = "\n".join(patch.splitlines()[-30:])
        return (
            "Patch failed during git apply:\n"
            f"{stderr.strip()}\n\n"
            "---- PATCH PREVIEW (last 30 lines) ----\n"
            f"{preview}"
        )