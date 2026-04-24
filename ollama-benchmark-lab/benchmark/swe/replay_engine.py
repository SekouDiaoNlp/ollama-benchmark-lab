from pathlib import Path


def run_replay(task, cache):

    cached = cache.get(task)

    print(f"[REPLAY DEBUG] cached raw type={type(cached)} value={cached}")

    if cached is not None:
        cached = Path(cached)

    print(f"[REPLAY DEBUG] cached normalized type={type(cached)} value={cached}")

    if cached is None or not cached.exists():
        print(f"[REPLAY DEBUG] MISSING CACHE for task={task}")
        raise FileNotFoundError(f"Missing cached replay for task={task}")

    return execute_from_cache(cached, task)


def execute_from_cache(cached: Path, task):

    print(f"[REPLAY DEBUG] executing cached={cached}")

    return {"ok": True}