from pathlib import Path


def extract_repo_context(repo_path: Path, max_files=5) -> str:
    """
    Lightweight heuristic: extract key files for prompt.
    """

    important_files = []

    for f in repo_path.rglob("*.py"):
        if len(important_files) >= max_files:
            break

        try:
            content = f.read_text()[:2000]
            important_files.append(f"\nFILE: {f}\n{content}\n")
        except Exception:
            continue

    return "\n".join(important_files)