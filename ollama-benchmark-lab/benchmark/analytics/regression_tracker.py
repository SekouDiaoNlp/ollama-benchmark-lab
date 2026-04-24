from collections import defaultdict


class RegressionTracker:
    """
    Tracks performance changes across runs.
    """

    def __init__(self):
        self.history = defaultdict(list)

    def record(self, model_name: str, result: dict):
        self.history[model_name].append(result)

    def detect_regressions(self, model_name: str):
        runs = self.history[model_name]

        if len(runs) < 2:
            return []

        regressions = []

        for prev, curr in zip(runs, runs[1:]):
            if prev["passed"] and not curr["passed"]:
                regressions.append({
                    "task_id": curr["task_id"],
                    "type": "performance_drop"
                })

        return regressions