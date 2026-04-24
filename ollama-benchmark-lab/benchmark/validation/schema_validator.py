"""
Schema validation for benchmark tasks.

This module provides the SchemaValidator class, which enforces strict structural
rules on task dictionaries to ensure compatibility with SWE-bench v2 standards.

Example:
    >>> validator = SchemaValidator()
    >>> result = validator.validate_task({"id": "1", "mode": "ACT", ...})
    >>> print(result["valid"])
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union, Type

from pydantic import ValidationError
from benchmark.validation.models import BaseTask, SWETask, PlanTask, ActTask, TaskMode


class SchemaValidator:
    """
    Pydantic-based validator (SWE-bench v2 compatible).
    Enforces strict structural rules using typed data models.

    Attributes:
        auto_repair (bool): If True, the validator may attempt to repair
            minor schema violations (not currently fully implemented).
    """

    def __init__(self, auto_repair: bool = False) -> None:
        """
        Initialize the validator.

        Args:
            auto_repair (bool): Flag indicating if automatic repair is enabled.
        """
        self.auto_repair: bool = auto_repair

    # =========================================================
    # PUBLIC API (NEW STANDARD)
    # =========================================================

    def validate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a task dictionary using Pydantic models.

        Args:
            task (Dict[str, Any]): The raw task configuration dictionary.

        Returns:
            Dict[str, Any]: A result dictionary containing 'valid' (bool) and 'errors' (List[str]).
        """
        mode_str = task.get("mode")
        
        # Select appropriate model based on mode
        model_map: Dict[str, Type[BaseTask]] = {
            TaskMode.SWE: SWETask,
            TaskMode.PLAN: PlanTask,
            TaskMode.ACT: ActTask,
        }
        
        model_class = model_map.get(mode_str, BaseTask)

        try:
            model_class.model_validate(task)
            return {
                "valid": True,
                "errors": []
            }
        except ValidationError as e:
            errors = [f"{err['loc'][-1]}:{err['type']}" for err in e.errors()]
            return {
                "valid": False,
                "errors": errors
            }

    # =========================================================
    # BACKWARD COMPATIBILITY LAYER
    # =========================================================

    def validate_file(self, path: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Legacy compatibility wrapper that accepts a file path or a dictionary.

        Args:
            path (Union[str, Path, Dict[str, Any]]): The path to a JSON file or a task dictionary.

        Returns:
            Dict[str, Any]: The validation result.
        """
        # If already dict → validate directly
        if isinstance(path, dict):
            return self.validate_task(path)

        # Otherwise treat as file path
        p: Path = Path(path)
        try:
            task: Dict[str, Any] = json.loads(p.read_text())
            return self.validate_task(task)
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"file_read_error:{str(e)}"]
            }