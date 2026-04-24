import subprocess
from pathlib import Path
import hashlib


class ImageBuilder:
    """
    Builds and caches Docker images per repo snapshot.
    """

    def __init__(self):
        self.prefix = "swebench"

    def _hash_repo(self, repo_path: Path):
        return hashlib.md5(str(repo_path).encode()).hexdigest()[:12]

    def image_name(self, repo_path: Path):
        return f"{self.prefix}:{self._hash_repo(repo_path)}"

    def image_exists(self, image: str) -> bool:
        result = subprocess.run(
            ["docker", "images", "-q", image],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())

    def build(self, repo_path: Path):
        image = self.image_name(repo_path)

        # ✅ CRITICAL: skip rebuild if exists
        if self.image_exists(image):
            return image

        dockerfile = """
        FROM python:3.12-slim
        WORKDIR /workspace
        COPY . .
        RUN pip install -q -e . || true
        """

        dockerfile_path = repo_path / "Dockerfile.autollama"
        dockerfile_path.write_text(dockerfile)

        subprocess.run(
            [
                "docker", "build",
                "-t", image,
                "-f", str(dockerfile_path),
                "."
            ],
            cwd=repo_path,
            check=True
        )

        return image