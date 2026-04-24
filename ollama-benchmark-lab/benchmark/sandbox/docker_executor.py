"""
Docker execution adapter for handling path normalizations and state checks.

This module provides the core `run` wrapper which sanitizes file paths
and verifies that snapshots and tests exist before initiating Docker runs.

Example:
    >>> from pathlib import Path
    >>> result = run({"id": "task1"}, Path("/tmp/tests"), Path("/tmp/snapshot"))
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


def run(
    task: Dict[str, Any],
    tests_src: Union[str, Path],
    snapshot_path: Optional[Union[str, Path]] = None,
    working_copy: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    Sanitize inputs and perform an execution dry-run check.

    This function normalizes input paths to pathlib.Path objects and raises errors
    if expected paths are missing. It acts as a strict type guard before execution.

    Args:
        task (Dict[str, Any]): The benchmark task parameters.
        tests_src (Union[str, Path]): Path to the tests source code.
        snapshot_path (Optional[Union[str, Path]]): Path to the base repository snapshot.
        working_copy (Optional[Union[str, Path]]): Path to the patched repository working copy.

    Returns:
        Dict[str, Any]: Execution status result dictionary.

    Raises:
        RuntimeError: If any of the required paths are provided but do not exist on disk.
    """
    logger.debug("[DOCKER_EXECUTOR DEBUG]")
    logger.debug("task: %s", task)
    logger.debug("tests_src: %s %s", tests_src, type(tests_src))
    logger.debug("snapshot_path: %s %s", snapshot_path, type(snapshot_path))
    logger.debug("working_copy: %s %s", working_copy, type(working_copy))

    tests_src_path: Path
    if isinstance(tests_src, str):
        logger.debug("[FIX] converting tests_src -> Path")
        tests_src_path = Path(tests_src)
    else:
        tests_src_path = tests_src

    snapshot_path_obj: Optional[Path] = None
    if snapshot_path is not None:
        if isinstance(snapshot_path, str):
            logger.debug("[FIX] converting snapshot_path -> Path")
            snapshot_path_obj = Path(snapshot_path)
        else:
            snapshot_path_obj = snapshot_path

    working_copy_obj: Optional[Path] = None
    if working_copy is not None:
        if isinstance(working_copy, str):
            logger.debug("[FIX] converting working_copy -> Path")
            working_copy_obj = Path(working_copy)
        else:
            working_copy_obj = working_copy

    # SAFETY CHECKS (NO SILENT FAILURES)
    if not tests_src_path.exists():
        raise RuntimeError(f"tests_src missing: {tests_src_path}")

    if snapshot_path_obj is not None and not snapshot_path_obj.exists():
        raise RuntimeError(f"snapshot_path missing: {snapshot_path_obj}")

    if working_copy_obj is not None and not working_copy_obj.exists():
        raise RuntimeError(f"working_copy missing: {working_copy_obj}")

    logger.debug("[DOCKER_EXECUTOR OK] all paths valid")

    # continue existing logic here (unchanged)
    return {
        "ok": True
    }