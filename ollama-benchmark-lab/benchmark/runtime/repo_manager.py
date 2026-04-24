"""
Repository checkout and validation manager.

This module provides the RepoManager class to facilitate checking out specific
commits of a git repository and guaranteeing the paths are valid `pathlib.Path` objects.

Example:
    >>> manager = RepoManager()
    >>> path = manager.get_repo("https://github.com/foo/bar.git", "main")
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class RepoManager:
    """
    Handles git repository checkouts and path normalization.
    """

    def get_repo(self, repo_url: str, commit: str) -> Path:
        """
        Check out a specific commit for a given repository and ensure the path exists.

        Args:
            repo_url (str): The URL of the remote git repository.
            commit (str): The commit hash or branch name to checkout.

        Returns:
            Path: The validated path to the local repository checkout.

        Raises:
            FileNotFoundError: If the checked out path does not exist on disk.
        """
        raw_repo_path: str = self._checkout(repo_url, commit)

        logger.debug("[REPO MANAGER DEBUG] raw repo_path type=%s value=%s", type(raw_repo_path), raw_repo_path)

        repo_path: Path = Path(raw_repo_path)

        logger.debug("[REPO MANAGER DEBUG] normalized repo_path type=%s value=%s", type(repo_path), repo_path)

        if not repo_path.exists():
            logger.error("[REPO MANAGER DEBUG] PATH DOES NOT EXIST: %s", repo_path)
            raise FileNotFoundError(f"Repository path not found: {repo_path}")

        logger.debug("[REPO MANAGER DEBUG] OK EXISTS: %s", repo_path)
        return repo_path

    def _checkout(self, repo_url: str, commit: str) -> str:
        """
        Simulate a checkout operation (internal placeholder).

        Args:
            repo_url (str): The target repository URL.
            commit (str): The target commit.

        Returns:
            str: The string representation of the expected checkout path.
        """
        path: str = f".cache/repos/{commit}"

        logger.debug("[REPO MANAGER DEBUG] checkout repo_url=%s commit=%s -> %s", repo_url, commit, path)

        return path