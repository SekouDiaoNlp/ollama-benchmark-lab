"""
Repository checkout and cache management.

This module provides the RepoManager class for managing local clones
of remote repositories used in benchmarks.
"""

import subprocess
from pathlib import Path
from typing import Union

# Default cache directory for cloned repositories
CACHE_DIR: Path = Path("/tmp/swe_repo_cache")
CACHE_DIR.mkdir(exist_ok=True, parents=True)

class RepoManager:
    """
    Manages local repository clones for replay execution.
    """

    def get_repo(self, repo_url: str) -> Path:
        """
        Ensure a repository is cloned locally and return its path.

        Args:
            repo_url (str): The URL of the repository to clone.

        Returns:
            Path: The path to the local repository clone.

        Raises:
            subprocess.CalledProcessError: If the git clone command fails.
        """
        # Create a stable directory name from the URL
        safe_name: str = repo_url.replace("/", "_").replace(":", "_").replace(".", "_")
        repo_path: Path = CACHE_DIR / safe_name

        if not repo_path.exists():
            subprocess.run([
                "git", "clone", repo_url, str(repo_path)
            ], check=True, capture_output=True)

        return repo_path