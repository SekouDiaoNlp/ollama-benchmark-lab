from _typeshed import Incomplete
from benchmark.cache.execution_cache import ExecutionCache as ExecutionCache
from benchmark.runtime.research_executor import run_research_task as run_research_task

cache: Incomplete

class ReplayEngine:
    def run(self, task: dict): ...
