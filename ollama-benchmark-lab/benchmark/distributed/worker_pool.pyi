from _typeshed import Incomplete
from benchmark.runtime.research_executor import run_research_task as run_research_task

class WorkerPool:
    workers: Incomplete
    queue: Incomplete
    def __init__(self, workers: int = 4) -> None: ...
    def run(self, tasks: list[dict]): ...
