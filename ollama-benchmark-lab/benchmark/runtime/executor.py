from pathlib import Path
from benchmark.runtime.dataset_loader import DatasetLoader


ROOT = Path(__file__).resolve().parents[2]
loader = DatasetLoader(ROOT)


def run_task(task_id_or_obj):
    """
    SWE-bench execution entrypoint.

    Supports:
    - task_id (str)
    - task dict (preloaded)
    """

    # -----------------------------------------
    # CASE 1: ID STRING
    # -----------------------------------------
    if isinstance(task_id_or_obj, str):
        task = loader.load_task(task_id_or_obj)

    # -----------------------------------------
    # CASE 2: DIRECT TASK OBJECT
    # -----------------------------------------
    elif isinstance(task_id_or_obj, dict):
        task = task_id_or_obj

    else:
        raise TypeError("task must be str or dict")

    # -----------------------------------------
    # SAFE FIELD ACCESS (schema-compliant)
    # -----------------------------------------
    tests = task.get("tests", {})
    execution = task.get("execution", {})

    tests_path = None
    entrypoint = None

    if isinstance(tests, dict):
        tests_path = tests.get("path")

    if isinstance(execution, dict):
        entrypoint = execution.get("entrypoint")

    # -----------------------------------------
    # DEBUG OUTPUT (temporary but safe)
    # -----------------------------------------
    return {
        "tests_path": tests_path,
        "entrypoint": entrypoint,
        "status": "loaded"
    }