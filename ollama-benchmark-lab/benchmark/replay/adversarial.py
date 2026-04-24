"""
Adversarial test case expansion for benchmark tasks.

This module provides utility functions for generating synthetic edge-case
prompts to test model robustness.
"""

from typing import Any, Dict, List

def generate_edge_cases(task: Dict[str, Any]) -> List[str]:
    """
    Generate a list of adversarial test expansion prompts based on the task.

    Args:
        task (Dict[str, Any]): The benchmark task configuration.

    Returns:
        List[str]: A list of expanded prompt strings with edge-case scenarios.
    """
    base: str = str(task.get("public_prompt", ""))

    return [
        f"{base}\nEdge case: empty input",
        f"{base}\nEdge case: null values",
        f"{base}\nEdge case: extremely large input"
    ]