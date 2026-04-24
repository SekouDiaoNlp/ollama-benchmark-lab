import subprocess

def apply_patch(repo_path, patch_text: str):
    p = subprocess.Popen(
        ["git", "apply"],
        cwd=repo_path,
        stdin=subprocess.PIPE,
        text=True
    )
    p.communicate(patch_text)

    if p.returncode != 0:
        raise RuntimeError("Patch failed to apply")