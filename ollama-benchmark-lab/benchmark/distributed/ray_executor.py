import ray
from benchmark.runtime.executor import run_task_instance


ray.init(ignore_reinit_error=True)


@ray.remote
def _run(task):
    return run_task_instance(task)


def run_all(tasks: list[dict]):
    futures = [_run.remote(t) for t in tasks]
    return ray.get(futures)