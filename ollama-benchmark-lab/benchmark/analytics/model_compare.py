class ModelComparator:
    """
    Compares performance across models.
    """

    def compare(self, model_a_results, model_b_results):
        a_pass = sum(r["passed"] for r in model_a_results)
        b_pass = sum(r["passed"] for r in model_b_results)

        total = len(model_a_results)

        return {
            "model_a_score": a_pass / total if total else 0,
            "model_b_score": b_pass / total if total else 0,
            "delta": (b_pass - a_pass) / total if total else 0
        }