from pathlib import Path


def run(task, tests_src, snapshot_path=None, working_copy=None):

    print("\n[DOCKER_EXECUTOR DEBUG]")
    print("task:", task)
    print("tests_src:", tests_src, type(tests_src))
    print("snapshot_path:", snapshot_path, type(snapshot_path))
    print("working_copy:", working_copy, type(working_copy))

    # HARD TYPE GUARDS (this is where your crash originates)
    if isinstance(tests_src, str):
        print("[FIX] converting tests_src -> Path")
        tests_src = Path(tests_src)

    if snapshot_path is not None and isinstance(snapshot_path, str):
        print("[FIX] converting snapshot_path -> Path")
        snapshot_path = Path(snapshot_path)

    if working_copy is not None and isinstance(working_copy, str):
        print("[FIX] converting working_copy -> Path")
        working_copy = Path(working_copy)

    # SAFETY CHECKS (NO SILENT FAILURES)
    if tests_src is not None and not tests_src.exists():
        raise RuntimeError(f"tests_src missing: {tests_src}")

    if snapshot_path is not None and not snapshot_path.exists():
        raise RuntimeError(f"snapshot_path missing: {snapshot_path}")

    if working_copy is not None and not working_copy.exists():
        raise RuntimeError(f"working_copy missing: {working_copy}")

    print("[DOCKER_EXECUTOR OK] all paths valid")

    # continue existing logic here (unchanged)
    return {
        "ok": True
    }