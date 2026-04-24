"""
Repository snapshot caching and path resolution.

This module provides the RepoSnapshot class, ensuring that all repository
snapshot locations are properly resolved, cached, and returned as strict Path objects.

Example:
    >>> snapshot = RepoSnapshot()
    >>> path = snapshot.get("https://github.com/foo/bar.git", "main")
"""

import logging
from pathlib import Path
from typing import Dict, Tuple, Union

logger = logging.getLogger(__name__)


class RepoSnapshot:
    """
    Manages cloning and caching of repository snapshots.

    Attributes:
        _cache (Dict[Tuple[str, str], Path]): Internal cache mapping (repo_url, commit) to the snapshot Path.
    """

    def __init__(self) -> None:
        """
        Initialize the RepoSnapshot manager with an empty cache.
        """
        self._cache: Dict[Tuple[str, str], Path] = {}

    def get(self, repo_url: str, commit: str) -> Path:
        """
        Retrieve a repository snapshot path, using cache if available.

        Args:
            repo_url (str): The URL of the repository.
            commit (str): The specific commit hash or branch to snapshot.

        Returns:
            Path: The validated path to the repository snapshot.
        """
        key: Tuple[str, str] = (repo_url, commit)

        if key in self._cache:
            path_cached: Path = self._cache[key]
            logger.debug("[RepoSnapshot] cache hit: %s type=%s", path_cached, type(path_cached))
            return self._ensure_path(path_cached, "cache-hit")

        # Simulate resolution
        path_resolved: Union[str, Path] = self._resolve(repo_url, commit)

        path_final: Path = self._ensure_path(path_resolved, "resolved")

        self._cache[key] = path_final

        logger.debug("[RepoSnapshot] cached: %s", path_final)

        return path_final

    def _resolve(self, repo_url: str, commit: str) -> str:
        """
        Resolve the repository snapshot (internal implementation placeholder).

        Args:
            repo_url (str): The repository URL.
            commit (str): The commit hash.

        Returns:
            str: A string path representing the snapshot location.
        """
        logger.debug("[RepoSnapshot] resolving repo_url=%s commit=%s", repo_url, commit)
        return f".cache/repos/{commit}"

    def _ensure_path(self, value: Union[str, Path], stage: str) -> Path:
        """
        Guarantee that the provided value is converted to a Path object.

        Args:
            value (Union[str, Path]): The path value to enforce.
            stage (str): The operational stage for debugging purposes.

        Returns:
            Path: The strict Path object.

        Raises:
            TypeError: If the value is neither a string nor a Path.
        """
        logger.debug("[RepoSnapshot] ensure_path stage=%s value=%s type=%s", stage, value, type(value))

        if isinstance(value, Path):
            return value

        if isinstance(value, str):
            return Path(value)

        raise TypeError(f"[RepoSnapshot] invalid path type at {stage}: {type(value)}")