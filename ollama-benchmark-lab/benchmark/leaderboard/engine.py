from collections import defaultdict


class Leaderboard:
    """
    Aggregates model performance across experiments.
    """

    def __init__(self):
        self.scores = defaultdict(list)

    def record(self, model_name: str, score: float):
        self.scores[model_name].append(score)

    def rank(self):
        return sorted(
            {
                model: sum(scores) / len(scores)
                for model, scores in self.scores.items()
            }.items(),
            key=lambda x: x[1],
            reverse=True
        )