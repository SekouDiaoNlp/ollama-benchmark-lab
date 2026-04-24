import random


class PatchMutationEngine:
    """
    Mutates patches to test overfitting robustness.
    """

    def mutate(self, patch: str):
        mutations = [
            lambda p: p.replace("==", "!="),
            lambda p: p + "\n# injected noise",
            lambda p: p.replace("0", "1"),
        ]

        mutated = random.choice(mutations)(patch)

        return {
            "mutated_patch": mutated,
            "mutation_type": "synthetic perturbation"
        }