import subprocess
import tempfile


def apply_patch(repo: str, patch: str) -> bool:
    try:
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(patch)
            path = f.name

        r = subprocess.run(["git", "apply", path], cwd=repo)
        return r.returncode == 0
    except:
        return False


def run_tests(repo: str, cmd: str) -> bool:
    try:
        r = subprocess.run(cmd, shell=True, cwd=repo, timeout=120)
        return r.returncode == 0
    except:
        return False