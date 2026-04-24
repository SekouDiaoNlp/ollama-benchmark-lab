"""
Data schema for SWE-bench tasks.

This module defines the SWETask dataclass for structured representation
of software engineering tasks.
"""

from dataclasses import dataclass

@dataclass
class SWETask:
    """
    Represents a software engineering task for benchmarking.

    Attributes:
        task_id (str): Unique identifier for the task.
        repo_url (str): URL of the target repository.
        commit (str): Target commit hash.
        entrypoint (str): Command to execute tests.
    """
    task_id: str
    repo_url: str
    commit: str
    entrypoint: str = "pytest -q"

    def validate(self) -> None:
        """
        Validate the task data integrity.

        Raises:
            AssertionError: If validation rules are violated.
        """
        assert self.repo_url.startswith("https://"), "repo_url must use HTTPS"
        assert len(self.commit) >= 6, "commit hash must be at least 6 characters"