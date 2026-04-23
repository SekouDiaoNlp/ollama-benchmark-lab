import json
from pathlib import Path


class CheckpointManager:

    def __init__(self, path: Path):
        self.path = path
        self.state = {}

        if path.exists():
            self._load()

    def _load(self):
        for line in self.path.read_text().splitlines():
            obj = json.loads(line)
            self.state[obj["key"]] = obj["value"]

    def save(self, key: str, value: dict):
        self.state[key] = value

        with self.path.open("a") as f:
            f.write(json.dumps({"key": key, "value": value}) + "\n")

    def done(self, key: str) -> bool:
        return key in self.state