"""
General utility functions for the benchmark suite.

This module provides common helpers such as configuration loading
with robust type handling and error recovery.
"""

import json
from pathlib import Path
from typing import Any, Dict, Union

def load_config(path: Union[str, Path, Dict[str, Any]] = "config.json") -> Dict[str, Any]:
    """
    Robustly load a configuration dictionary from a file or directly from input.

    This function prevents common 'str' vs 'Path' attribute errors by
    normalizing types and checking existence before reading.

    Args:
        path (Union[str, Path, Dict[str, Any]]): A file path or an already loaded dict.
            Defaults to 'config.json'.

    Returns:
        Dict[str, Any]: The loaded configuration dictionary or an empty dict if missing/invalid.
    """
    # If already a config dict → return directly
    if isinstance(path, dict):
        return path

    # Normalize input to Path object
    p: Path = Path(path)

    if not p.exists():
        return {}

    try:
        data: Dict[str, Any] = json.loads(p.read_text())
        return data
    except Exception:
        # Return empty config if parsing fails
        return {}