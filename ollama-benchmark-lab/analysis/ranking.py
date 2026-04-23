import numpy as np


def rank_stability(scores):
    ranks = []

    for _ in range(500):
        sampled = {m: np.mean(np.random.choice(v, len(v), True))
                   for m, v in scores.items()}

        ranks.append(sorted(sampled, key=sampled.get, reverse=True))

    return ranks