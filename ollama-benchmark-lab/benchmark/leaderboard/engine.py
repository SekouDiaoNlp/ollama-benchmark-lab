"""
Model performance leaderboard engine.

This module provides the Leaderboard class for aggregating and ranking
model performance across multiple benchmark experiments.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

class Leaderboard:
    """
    Aggregates model performance scores and computes rankings.

    Attributes:
        scores (Dict[str, List[float]]): Mapping of model names to lists of historical scores.
    """

    def __init__(self) -> None:
        """
        Initialize the leaderboard with empty scores.
        """
        self.scores: Dict[str, List[float]] = defaultdict(list)

    def record(self, model_name: str, score: float) -> None:
        """
        Record a new evaluation score for a specific model.

        Args:
            model_name (str): The name of the model.
            score (float): The evaluation score to record.
        """
        self.scores[model_name].append(score)

    def rank(self) -> List[Tuple[str, float]]:
        """
        Compute the mean score for each model and return a ranked list.

        Returns:
            List[Tuple[str, float]]: A list of (model_name, mean_score) tuples,
                sorted by score in descending order.
        """
        ranking: List[Tuple[str, float]] = sorted(
            {
                model: sum(scores) / len(scores)
                for model, scores in self.scores.items()
                if scores
            }.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return ranking