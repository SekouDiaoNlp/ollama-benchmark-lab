"""
Patch mutation engine for robustness testing.

This module provides the PatchMutationEngine class which randomly mutates
valid patches to simulate syntax and semantic noise.

Example:
    >>> engine = PatchMutationEngine()
    >>> res = engine.mutate("foo == bar")
"""

import random
from typing import Any, Callable, Dict, List


class PatchMutationEngine:
    """
    Mutates patches to test overfitting robustness.
    """

    def mutate(self, patch: str) -> Dict[str, Any]:
        """
        Apply a random mutation to the provided patch string.

        Args:
            patch (str): The original patch text.

        Returns:
            Dict[str, Any]: The mutated patch and the mutation strategy type.
        """
        mutations: List[Callable[[str], str]] = [
            lambda p: p.replace("==", "!="),
            lambda p: p + "\n# injected noise",
            lambda p: p.replace("0", "1"),
        ]

        mutated: str = random.choice(mutations)(patch)

        return {
            "mutated_patch": mutated,
            "mutation_type": "synthetic perturbation"
        }