import json
from pathlib import Path


class SWEBenchLoader:
    """
    Loads SWE-bench compatible tasks (repo + commit + tests).
    """

    def __init__(self, root="tasks"):
        self.root = Path(root)

    def load_all(self) -> list[dict]:
        tasks = []

        for f in self.root.rglob("*.json"):
            data = json.loads(f.read_text())

            # HARD REQUIREMENTS (SWE-bench mode)
            if "repo_url" not in data:
                continue
            if "commit" not in data:
                continue

            data["task_id"] = data.get("task_id") or f.stem
            tasks.append(data)

        return tasks