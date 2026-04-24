import subprocess
from pathlib import Path
import hashlib


class ImageBuilder:
    """
    Builds cached Docker images per repo snapshot.
    """

    def __init__(self):
        self.prefix = "swebench"

    def _hash_repo(self, repo_path: Path):
        return hashlib.md5(str(repo_path).encode()).hexdigest()[:10]

    def image_name(self, repo_path: Path):
        return f"{self.prefix}:{self._hash_repo(repo_path)}"

    def build(self, repo_path: Path):
        image = self.image_name(repo_path)

        dockerfile = f"""
        FROM python:3.12-slim
        WORKDIR /workspace
        COPY . .
        RUN pip install -q -e . || true
        """

        dockerfile_path = repo_path / "Dockerfile.autollama"
        dockerfile_path.write_text(dockerfile)

        subprocess.run(
            ["docker", "build", "-t", image, "-f", str(dockerfile_path), "."],
            cwd=repo_path,
            check=True
        )

        return image