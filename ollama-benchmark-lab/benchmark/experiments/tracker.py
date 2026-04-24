import time
import uuid


class ExperimentTracker:
    """
    Lightweight experiment tracking system.
    """

    def __init__(self):
        self.runs = {}

    def start_run(self, config: dict):
        run_id = str(uuid.uuid4())

        self.runs[run_id] = {
            "config": config,
            "start_time": time.time(),
            "results": []
        }

        return run_id

    def log_result(self, run_id: str, result: dict):
        self.runs[run_id]["results"].append(result)

    def end_run(self, run_id: str):
        self.runs[run_id]["end_time"] = time.time()
        return self.runs[run_id]