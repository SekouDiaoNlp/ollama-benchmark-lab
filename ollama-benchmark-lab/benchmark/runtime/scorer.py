def score_result(result: dict) -> int:
    return 1 if result.get("status") == "passed" else 0


def aggregate(results: list[dict]):
    scores = [score_result(r) for r in results]

    return {
        "total": len(results),
        "passed": sum(scores),
        "pass_rate": sum(scores) / len(results) if results else 0.0
    }