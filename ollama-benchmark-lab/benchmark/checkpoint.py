import json
from pathlib import Path


class CheckpointManager:

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.state = {}

        if self.path.exists():
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