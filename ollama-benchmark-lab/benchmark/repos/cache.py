"""
Repository snapshot caching system.

This module provides the RepoCache class for managing local filesystem paths
to repository snapshots indexed by URL and commit hash.
"""

from pathlib import Path
from typing import Union

class RepoCache:
    """
    Manages the mapping of repository snapshots to local filesystem paths.

    Attributes:
        base_dir (Path): The root directory for storing snapshots.
    """

    def __init__(self, base_dir: Union[str, Path] = ".cache/repo_snapshots") -> None:
        """
        Initialize the repository cache.

        Args:
            base_dir (Union[str, Path]): Root directory for snapshot storage.
        """
        self.base_dir: Path = Path(base_dir)

    def snapshot_path(self, repo_url: str, commit: str) -> Path:
        """
        Compute the unique filesystem path for a specific repository snapshot.

        Args:
            repo_url (str): The URL of the repository.
            commit (str): The commit hash.

        Returns:
            Path: The resolved local path for the snapshot.
        """
        # Create a safe name from the repository URL
        safe_repo_name: str = repo_url.replace("/", "_").replace(":", "_")
        snapshot_dir: Path = self.base_dir / safe_repo_name / commit

        return snapshot_dir