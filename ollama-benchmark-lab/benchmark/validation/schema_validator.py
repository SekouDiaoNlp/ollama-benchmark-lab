import json
from pathlib import Path


class SchemaValidator:
    """
    Dict-based validator (SWE-bench v2 compatible).
    NO file-path coupling inside validation logic.
    """

    def __init__(self, auto_repair: bool = False):
        self.auto_repair = auto_repair

    # =========================================================
    # PUBLIC API (NEW STANDARD)
    # =========================================================

    def validate_task(self, task: dict):
        """
        Validate a task dictionary directly.
        """

        errors = []

        # -------------------------
        # REQUIRED TOP-LEVEL FIELDS
        # -------------------------
        for key in ["id", "mode", "public_prompt", "version"]:
            if key not in task or task[key] in (None, ""):
                errors.append(f"missing:{key}")

        # -------------------------
        # MODE CHECK
        # -------------------------
        if task.get("mode") not in {"ACT", "PLAN", "SWE"}:
            errors.append("invalid:mode")

        # -------------------------
        # TESTS (NEW SCHEMA FORMAT)
        # -------------------------
        tests = task.get("tests", {})

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
        execution = task.get("execution", {})

        if not isinstance(execution, dict):
            errors.append("execution invalid type")
        else:
            if not execution.get("entrypoint"):
                errors.append("execution.entrypoint missing")

        # -------------------------
        # RUBRIC (OPTIONAL)
        # -------------------------
        rubric = task.get("rubric", {})
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
    # BACKWARD COMPATIBILITY LAYER (OPTION A FIX)
    # =========================================================

    def validate_file(self, path):
        """
        Legacy compatibility:
        - accepts file path OR dict
        - prevents pipeline breakage
        """

        # If already dict → validate directly
        if isinstance(path, dict):
            return self.validate_task(path)

        # Otherwise treat as file path
        p = Path(path)
        task = json.loads(p.read_text())

        return self.validate_task(task)