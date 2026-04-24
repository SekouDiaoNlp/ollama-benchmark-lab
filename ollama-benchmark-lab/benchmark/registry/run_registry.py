"""
Execution history registry for benchmark experiments.

This module provides the RunRegistry class for storing and querying
detailed metadata about all benchmark runs executed in the current session.
"""

from typing import Any, Dict, List

class RunRegistry:
    """
    In-memory storage for benchmark execution metadata.

    Attributes:
        registry (List[Dict[str, Any]]): A list of execution record dictionaries.
    """

    def __init__(self) -> None:
        """
        Initialize an empty run registry.
        """
        self.registry: List[Dict[str, Any]] = []

    def add(self, run: Dict[str, Any]) -> None:
        """
        Add a new execution record to the registry.

        Args:
            run (Dict[str, Any]): The run metadata dictionary.
        """
        self.registry.append(run)

    def query_by_model(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Retrieve all execution records associated with a specific model.

        Args:
            model_name (str): The name of the model to filter by.

        Returns:
            List[Dict[str, Any]]: A list of matching execution records.
        """
        return [
            r for r in self.registry
            if r.get("config", {}).get("model") == model_name
        ]