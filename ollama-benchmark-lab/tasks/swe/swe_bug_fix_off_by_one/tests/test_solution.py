import sys
from pathlib import Path
import importlib.util
import pytest


# =========================================================
# LOCATE TASK ROOT
# =========================================================

TASK_ROOT = Path(__file__).resolve().parents[1]
SOLUTION_PATH = TASK_ROOT / "solution.py"


# =========================================================
# DYNAMIC IMPORT SANDBOX (NO PYTHONPATH RELIANCE)
# =========================================================

def load_solution():
    if not SOLUTION_PATH.exists():
        raise FileNotFoundError(f"Missing solution.py at {SOLUTION_PATH}")

    spec = importlib.util.spec_from_file_location(
        "solution",
        SOLUTION_PATH
    )

    module = importlib.util.module_from_spec(spec)
    sys.modules["solution"] = module
    spec.loader.exec_module(module)

    return module


solution = load_solution()


# =========================================================
# TESTS
# =========================================================

def test_fix_off_by_one_basic():
    """
    Basic correctness test for SWE bug fix.
    """
    result = solution.fix_off_by_one([1, 2, 3])

    assert isinstance(result, list)
    assert len(result) == len([1, 2, 3])


def test_fix_off_by_one_edge():
    """
    Edge case validation.
    """
    result = solution.fix_off_by_one([])

    assert result == []