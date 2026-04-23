import numpy as np


def bootstrap_ci(data, n=1000):

    means = []

    for _ in range(n):
        sample = np.random.choice(data, size=len(data), replace=True)
        means.append(np.mean(sample))

    return np.percentile(means, [2.5, 97.5])