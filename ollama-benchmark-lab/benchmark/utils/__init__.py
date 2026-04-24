import json
from pathlib import Path
from typing import Dict, Any, Union


def load_config(path: Union[str, Path, Dict[str, Any]] = "config.json") -> Dict[str, Any]:
    """
    Robust config loader.

    Supports:
    - dict input (returned as-is)
    - string path
    - Path object

    Prevents: 'str' object has no attribute 'exists'
    """

    # already a config dict → return directly
    if isinstance(path, dict):
        return path

    # normalize to Path
    p = Path(path)

    if not p.exists():
        return {}

    try:
        return json.loads(p.read_text())
    except Exception:
        return {}