import ray
from benchmark.replay.engine import ReplayEngine

ray.init(ignore_reinit_error=True)

engine = ReplayEngine()

@ray.remote
def run_task(task):
    return engine.run_task(task)