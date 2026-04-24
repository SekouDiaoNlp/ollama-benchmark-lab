import subprocess
from pathlib import Path

CACHE_DIR = Path("cache/repos")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_repo(repo_url: str, commit: str) -> Path:
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = CACHE_DIR / repo_name

    # Clone if missing
    if not repo_path.exists():
        subprocess.run(
            ["git", "clone", repo_url, str(repo_path)],
            check=True
        )

    # Checkout correct commit
    subprocess.run(
        ["git", "checkout", commit],
        cwd=repo_path,
        check=True
    )

    return repo_path