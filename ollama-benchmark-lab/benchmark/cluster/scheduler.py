import ray
from benchmark.cluster.ray_worker import run_task

class Scheduler:

    def run(self, tasks):
        futures = [run_task.remote(t) for t in tasks]
        return ray.get(futures)