from collections import Counter


class FailureClusterer:
    """
    Groups failures by error pattern.
    """

    def cluster(self, results: list[dict]):
        errors = []

        for r in results:
            if not r.get("passed"):
                stderr = r.get("stderr", "")
                errors.append(stderr.splitlines()[-1] if stderr else "unknown")

        return Counter(errors)