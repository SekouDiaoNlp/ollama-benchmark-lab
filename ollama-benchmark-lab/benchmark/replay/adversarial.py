def generate_edge_cases(task):
    """
    Placeholder for LLM-based adversarial test expansion.
    """
    base = task.get("public_prompt", "")

    return [
        base + "\nEdge case: empty input",
        base + "\nEdge case: null values",
        base + "\nEdge case: extremely large input"
    ]