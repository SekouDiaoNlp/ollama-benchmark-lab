LOCAL_MODELS = {
    "coder": [
        "qwen2.5-coder:7b-noyap",
        "qwen2.5-coder:3b-noyap",
        "codellama:7b-instruct-noyap",
        "codegemma:7b-acting-noyap",
        "starcoder2:7b-acting-noyap",
    ]
}


def resolve_model(preferred: str | None = None) -> str:
    """
    Enforces local-only execution.
    """

    if preferred and preferred in sum(LOCAL_MODELS.values(), []):
        return preferred

    # default safe model
    return "qwen2.5-coder:7b-noyap"