"""
Registry for resolving and enforcing local-only LLM execution.

This module guarantees that the evaluation harness NEVER calls out to
remote APIs (e.g. OpenAI), explicitly restricting runs to a predefined
list of compatible local Ollama models.

Example:
    >>> model = resolve_model("codegemma:7b-acting-noyap")
"""

from typing import Dict, List, Optional


LOCAL_MODELS: Dict[str, List[str]] = {
    "coder": [
        "qwen2.5-coder:7b-noyap",
        "qwen2.5-coder:3b-noyap",
        "codellama:7b-instruct-noyap",
        "codegemma:7b-acting-noyap",
        "starcoder2:7b-acting-noyap",
    ]
}


def resolve_model(preferred: Optional[str] = None) -> str:
    """
    Resolve a model name, strictly enforcing local-only execution.

    Args:
        preferred (Optional[str]): The user's requested model name. Defaults to None.

    Returns:
        str: The resolved model name. If the preferred model is not in the allowed list,
            a default safe model ('qwen2.5-coder:7b-noyap') is returned instead.
    """
    allowed_models: List[str] = sum(LOCAL_MODELS.values(), [])

    if preferred is not None and preferred in allowed_models:
        return preferred

    # default safe model
    return "qwen2.5-coder:7b-noyap"