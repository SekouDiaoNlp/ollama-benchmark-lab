import json
from pathlib import Path


class SWEBenchLoader:
    """
    Loads SWE-bench style dataset with strict schema normalization.
    """

    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)

    def load_all(self):
        tasks = []

        for file in self.dataset_path.rglob("*.json"):
            task = json.loads(file.read_text())

            tasks.append(self._normalize(task))

        return tasks

    def _normalize(self, task: dict):
        """
        Enforce SWE-bench canonical structure.
        """

        return {
            "id": task.get("id"),
            "repo": task["repo"],
            "base_commit": task["base_commit"],
            "patch": task.get("patch"),
            "tests": {
                "path": task.get("tests", {}).get("path")
            },
            "execution": {
                "entrypoint": task.get("execution", {}).get("entrypoint", "pytest -q")
            }
        }