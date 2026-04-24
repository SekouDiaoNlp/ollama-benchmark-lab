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
from typing import Any, Dict, List, Union


class SchemaValidator:
    """
    Dict-based validator (SWE-bench v2 compatible).
    NO file-path coupling inside validation logic.

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
        Validate a task dictionary directly against the required schema.

        Args:
            task (Dict[str, Any]): The raw task configuration dictionary.

        Returns:
            Dict[str, Any]: A result dictionary containing 'valid' (bool) and 'errors' (List[str]).
        """
        errors: List[str] = []

        # -------------------------
        # REQUIRED TOP-LEVEL FIELDS
        # -------------------------
        for key in ["id", "mode", "public_prompt", "version"]:
            if key not in task or task[key] in (None, ""):
                errors.append(f"missing:{key}")

        # -------------------------
        # MODE CHECK
        # -------------------------
        if str(task.get("mode", "")) not in {"ACT", "PLAN", "SWE"}:
            errors.append("invalid:mode")

        # -------------------------
        # TESTS (NEW SCHEMA FORMAT)
        # -------------------------
        tests: Any = task.get("tests", {})

        if isinstance(tests, str):
            errors.append("tests must be object with path")

        elif isinstance(tests, dict):
            if not tests.get("path"):
                errors.append("tests.path missing")

        else:
            errors.append("tests invalid type")

        # -------------------------
        # EXECUTION BLOCK
        # -------------------------
        execution: Any = task.get("execution", {})

        if not isinstance(execution, dict):
            errors.append("execution invalid type")
        else:
            if not execution.get("entrypoint"):
                errors.append("execution.entrypoint missing")

        # -------------------------
        # RUBRIC (OPTIONAL)
        # -------------------------
        rubric: Any = task.get("rubric", {})
        if rubric and isinstance(rubric, dict):
            allowed = {"correctness", "structure", "edge_cases", "efficiency"}
            for k in rubric:
                if k not in allowed:
                    errors.append(f"rubric.invalid:{k}")

        return {
            "valid": len(errors) == 0,
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
        task: Dict[str, Any] = json.loads(p.read_text())

        return self.validate_task(task)