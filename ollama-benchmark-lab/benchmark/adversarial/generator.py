def generate_adversarial_cases(task: dict):
    """
    Minimal adversarial augmentation layer.
    """

    base = [
        {"case": "empty input"},
        {"case": "large input"},
        {"case": "negative values"},
        {"case": "malformed structure"}
    ]

    return {
        "task_id": task["id"],
        "cases": base
    }