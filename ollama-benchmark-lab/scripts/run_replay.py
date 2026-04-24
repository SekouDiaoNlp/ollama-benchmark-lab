from benchmark.dataset.loader import SWEBenchDataset
from benchmark.cluster.scheduler import Scheduler

dataset = SWEBenchDataset().load()

scheduler = Scheduler()

results = scheduler.run(dataset)

print("\n=== RESULTS ===")
for r in results:
    print(r)