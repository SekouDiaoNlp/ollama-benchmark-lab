import subprocess


def apply_patch(repo_path, patch_text: str):
    """
    Applies a unified diff patch to a repo.
    """

    proc = subprocess.run(
        ["git", "apply"],
        input=patch_text,
        text=True,
        cwd=repo_path,
        capture_output=True
    )

    if proc.returncode != 0:
        raise RuntimeError(
            f"Patch failed:\n{proc.stderr}"
        )