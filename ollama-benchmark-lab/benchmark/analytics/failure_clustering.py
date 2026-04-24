"""
Failure grouping and pattern recognition.

This module provides the FailureClusterer, which scans execution results
to bucket failing runs by their exact error signatures.

Example:
    >>> clusterer = FailureClusterer()
    >>> counts = clusterer.cluster([{"passed": False, "stderr": "ValueError: bad"}])
"""

from collections import Counter
from typing import Any, Dict, List


class FailureClusterer:
    """
    Groups failures by error pattern.
    """

    def cluster(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Cluster failures by extracting the final line of standard error.

        Args:
            results (List[Dict[str, Any]]): Normalized execution results.

        Returns:
            Dict[str, int]: Frequencies of each unique error signature.
        """
        errors: List[str] = []

        for r in results:
            if not r.get("passed"):
                stderr: str = str(r.get("stderr", ""))
                errors.append(stderr.splitlines()[-1] if stderr else "unknown")

        return dict(Counter(errors))