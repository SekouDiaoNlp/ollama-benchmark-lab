from benchmark.cache.execution_cache import ExecutionCache
from benchmark.runtime.research_executor import run_research_task


cache = ExecutionCache()


class ReplayEngine:
    """
    Replays SWE-bench runs deterministically.
    """

    def run(self, task: dict):
        if cache.exists(task):
            return cache.load(task)

        result = run_research_task(task)
        cache.save(task, result)

        return result