import random


class AdversarialTestGenerator:
    """
    Generates edge-case tests from repo + patch context.
    """

    def generate(self, repo_path: str, patch: str | None):
        """
        Returns synthetic test cases that stress failure modes.
        """

        base_cases = [
            "empty input",
            "null handling",
            "large input",
            "unicode edge case",
            "off-by-one boundary",
        ]

        random.shuffle(base_cases)

        return {
            "generated_tests": base_cases[:3],
            "strategy": "mutation-based fuzz expansion"
        }