class SWEBenchEvaluator:
    """
    Computes SWE-bench style correctness metrics.
    """

    def evaluate(self, result: dict):
        output = result.get("result", {})

        passed = output.get("exit_code") == 0

        return {
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "stdout_tail": output.get("stdout", "")[-500:],
            "stderr_tail": output.get("stderr", "")[-500:],
        }