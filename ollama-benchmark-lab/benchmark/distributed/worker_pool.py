import multiprocessing as mp
from queue import Queue
from benchmark.runtime.research_executor import run_research_task


class WorkerPool:
    """
    Lightweight distributed execution without Ray.
    """

    def __init__(self, workers=4):
        self.workers = workers
        self.queue = Queue()

    def _worker(self):
        while True:
            task = self.queue.get()
            if task is None:
                break
            run_research_task(task)

    def run(self, tasks: list[dict]):
        processes = []

        for _ in range(self.workers):
            p = mp.Process(target=self._worker)
            p.start()
            processes.append(p)

        for t in tasks:
            self.queue.put(t)

        for _ in processes:
            self.queue.put(None)

        for p in processes:
            p.join()