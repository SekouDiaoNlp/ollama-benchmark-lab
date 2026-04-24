"""
Client wrapper for local Ollama execution.

This module provides the OllamaClient, which interfaces with local models
via the OllamaEngine.
"""

from benchmark.llm.engine import OllamaEngine


class OllamaClient:
    """
    A local client for running inference via the Ollama command line interface.
    """

    def __init__(self) -> None:
        self.engine: OllamaEngine = OllamaEngine()

    def run(self, model: str, prompt: str) -> str:
        """
        Execute a prompt against a local Ollama model.

        Args:
            model (str): The name of the model to run.
            prompt (str): The prompt text to send to the model.

        Returns:
            str: The generated output text.
        """
        return self.engine.generate(model, prompt)