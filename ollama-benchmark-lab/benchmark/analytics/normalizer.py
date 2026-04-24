class ResultNormalizer:
    """
    Converts raw execution results into stable benchmark schema.
    """

    def normalize(self, task_id: str, result: dict):
        return {
            "task_id": task_id,
            "passed": result.get("score", {}).get("passed", False),
            "exit_code": result.get("baseline", {}).get("result", {}).get("exit_code"),
            "stdout": result.get("baseline", {}).get("result", {}).get("stdout", ""),
            "stderr": result.get("baseline", {}).get("result", {}).get("stderr", ""),
            "timestamp": result.get("timestamp"),
        }