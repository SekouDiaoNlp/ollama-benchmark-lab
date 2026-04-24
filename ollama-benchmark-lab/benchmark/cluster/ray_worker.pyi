import ray
from _typeshed import Incomplete
from benchmark.replay.engine import ReplayEngine as ReplayEngine

engine: Incomplete

@ray.remote
def run_task(task): ...
