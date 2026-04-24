from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RepoSnapshot:
    """
    Ensures repo snapshot paths are ALWAYS Path objects.
    """

    def __init__(self):
        self._cache = {}

    def get(self, repo_url: str, commit: str) -> Path:
        key = (repo_url, commit)

        if key in self._cache:
            path = self._cache[key]
            logger.debug(f"[RepoSnapshot] cache hit: {path} type={type(path)}")
            return self._ensure_path(path, "cache-hit")

        # simulate resolution (your existing logic)
        path = self._resolve(repo_url, commit)

        path = self._ensure_path(path, "resolved")

        self._cache[key] = path

        logger.debug(f"[RepoSnapshot] cached: {path}")

        return path

    def _resolve(self, repo_url: str, commit: str):
        """
        IMPORTANT: THIS MAY RETURN str OR Path depending on implementation.
        That is the BUG SOURCE.
        """
        # DEBUG TRACE
        logger.debug(f"[RepoSnapshot] resolving repo_url={repo_url} commit={commit}")

        # placeholder for your real logic
        return f".cache/repos/{commit}"

    def _ensure_path(self, value, stage: str) -> Path:
        """
        HARD GUARANTEE: everything becomes Path.
        """

        logger.debug(f"[RepoSnapshot] ensure_path stage={stage} value={value} type={type(value)}")

        if isinstance(value, Path):
            return value

        if isinstance(value, str):
            return Path(value)

        raise TypeError(f"[RepoSnapshot] invalid path type at {stage}: {type(value)}")