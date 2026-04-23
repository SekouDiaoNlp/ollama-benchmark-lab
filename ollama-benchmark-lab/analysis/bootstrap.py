import numpy as np


def bootstrap_ci(values, n=1000):
    values = np.array(values)

    means = []
    for _ in range(n):
        sample = np.random.choice(values, len(values), True)
        means.append(sample.mean())

    return float(np.mean(values)), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))