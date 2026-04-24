import json
from pathlib import Path

class SWEBenchDataset:
    def __init__(self, path="tasks"):
        self.path = Path(path)

    def load(self):
        tasks = []
        for f in self.path.rglob("task.json"):
            with open(f) as fp:
                data = json.load(fp)
                data["__path"] = str(f.parent)
                tasks.append(data)
        return tasks