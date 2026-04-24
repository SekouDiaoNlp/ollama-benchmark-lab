"""
Docker image builder and caching utility.

This module provides the ImageBuilder class, responsible for taking a snapshot
of a code repository, generating a deterministic hash, and building a Docker
image to execute code within that environment.

Example:
    >>> builder = ImageBuilder()
    >>> image_name = builder.build(Path("/tmp/my_repo"))
"""

import hashlib
import subprocess
from pathlib import Path


class ImageBuilder:
    """
    Builds and caches Docker images dynamically per repository snapshot.

    Attributes:
        prefix (str): The prefix used to tag Docker images.
    """

    def __init__(self) -> None:
        """
        Initialize the ImageBuilder.
        """
        self.prefix: str = "swebench"

    def _hash_repo(self, repo_path: Path) -> str:
        """
        Generate a unique MD5 hash based on the repository path.

        Args:
            repo_path (Path): The file system path to the repository.

        Returns:
            str: A 12-character hexadecimal hash string.
        """
        return hashlib.md5(str(repo_path).encode()).hexdigest()[:12]

    def image_name(self, repo_path: Path) -> str:
        """
        Construct the Docker image name based on the repository hash.

        Args:
            repo_path (Path): The file system path to the repository.

        Returns:
            str: The fully formatted Docker image name.
        """
        return f"{self.prefix}:{self._hash_repo(repo_path)}"

    def image_exists(self, image: str) -> bool:
        """
        Check if a Docker image already exists locally.

        Args:
            image (str): The name or tag of the Docker image to query.

        Returns:
            bool: True if the image exists, False otherwise.
        """
        result = subprocess.run(
            ["docker", "images", "-q", image],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())

    def build(self, repo_path: Path) -> str:
        """
        Build a Docker image from a given repository path.

        If the image already exists locally, this method safely skips the build process.

        Args:
            repo_path (Path): The file system path containing the repository.

        Returns:
            str: The name of the built Docker image.

        Raises:
            subprocess.CalledProcessError: If the 'docker build' command fails.
        """
        image: str = self.image_name(repo_path)

        # Skip rebuild if image exists
        if self.image_exists(image):
            return image

        dockerfile: str = (
            "FROM python:3.12-slim\n"
            "WORKDIR /workspace\n"
            "COPY . .\n"
            "RUN pip install -q -e . || true\n"
        )

        dockerfile_path: Path = repo_path / "Dockerfile.autollama"
        dockerfile_path.write_text(dockerfile)

        subprocess.run(
            [
                "docker", "build",
                "-t", image,
                "-f", str(dockerfile_path),
                "."
            ],
            cwd=str(repo_path),
            check=True
        )

        return image