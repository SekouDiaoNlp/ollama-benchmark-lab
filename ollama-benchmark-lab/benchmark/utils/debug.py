"""
Debug utilities for path verification and stack tracing.

This module provides functions to inspect variable types and values,
specifically for ensuring correct Path vs string usage across the codebase.
"""

from pathlib import Path
import traceback
from typing import Any, Union

def debug_path(name: str, value: Any) -> None:
    """
    Log type, value, and stack trace to debug path-related issues.

    Args:
        name (str): The identifier for the variable being debugged.
        value (Any): The current value of the variable.
    """
    print("\n" + "=" * 80)
    print(f"[DEBUG PATH] {name}")
    print(f"TYPE: {type(value)}")
    print(f"VALUE: {value}")

    # Highlight potential string/Path confusion
    if isinstance(value, str):
        print("⚠️ WARNING: VALUE IS STRING (expected Path)")

    print("STACK TRACE:")
    traceback.print_stack(limit=8)
    print("=" * 80 + "\n")

def ensure_path(value: Union[str, Path], name: str = "unknown") -> Path:
    """
    Ensure a value is a Path object, logging a debug message if conversion is required.

    Args:
        value (Union[str, Path]): The value to verify or convert.
        name (str): Name of the variable for debugging purposes.

    Returns:
        Path: The guaranteed Path object.
    """
    if isinstance(value, str):
        debug_path(name, value)
        return Path(value)

    return value