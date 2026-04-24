from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List


REQUIRED_FIELDS = [
    "id",
    "mode",
    "public_prompt",
    "version"
]


class SchemaValidator:

    def __init__(self, auto_repair: bool = True):
        self.auto_repair = auto_repair

    # =====================================================
    # PUBLIC API
    # =====================================================

    def validate_file(self, path: Path) -> Dict[str, Any]:
        try:
            data = json.loads(path.read_text())
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"invalid_json:{e}"]
            }

        errors = self._validate_fields(data)

        repaired = False

        if errors and self.auto_repair:
            repaired = self._auto_repair(data)

            if repaired:
                # re-validate after repair
                errors = self._validate_fields(data)

                if not errors:
                    path.write_text(json.dumps(data, indent=2))

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "repaired": repaired
        }

    # =====================================================
    # VALIDATION
    # =====================================================

    def _validate_fields(self, data: Dict[str, Any]) -> List[str]:
        errors = []

        for field in REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"missing_field:{field}")

        # validate mode
        if "mode" in data:
            if data["mode"] not in ["PLAN", "ACT", "SWE"]:
                errors.append("invalid_mode")

        return errors

    # =====================================================
    # AUTO REPAIR
    # =====================================================

    def _auto_repair(self, data: Dict[str, Any]) -> bool:
        changed = False

        # migrate prompt → public_prompt
        if "public_prompt" not in data:
            if "prompt" in data:
                data["public_prompt"] = data["prompt"]
                changed = True

        # default version
        if "version" not in data:
            data["version"] = "1.0"
            changed = True

        # generate id if missing
        if "id" not in data:
            data["id"] = self._generate_id(data)
            changed = True

        # normalize mode
        if "mode" in data:
            data["mode"] = data["mode"].upper()

        # add hash (for dataset versioning)
        if "hash" not in data:
            data["hash"] = self._compute_hash(data)
            changed = True

        return changed

    # =====================================================
    # HELPERS
    # =====================================================

    def _generate_id(self, data: Dict[str, Any]) -> str:
        base = data.get("public_prompt", "")[:30]
        return base.replace(" ", "_").lower()

    def _compute_hash(self, data: Dict[str, Any]) -> str:
        payload = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()