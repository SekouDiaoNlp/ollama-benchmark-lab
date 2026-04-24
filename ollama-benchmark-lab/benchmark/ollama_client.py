"""
Client wrapper for local Ollama execution.

This module provides the OllamaClient, which interfaces directly with the
Ollama CLI to run inference on local models using standard input and output streams.

Example:
    >>> client = OllamaClient()
    >>> output = client.run("codegemma:2b", "Write a python function")
"""

import subprocess


class OllamaClient:
    """
    A local client for running inference via the Ollama command line interface.
    """

    def run(self, model: str, prompt: str) -> str:
        """
        Execute a prompt against a local Ollama model.

        Args:
            model (str): The name of the model to run (e.g., 'codegemma:2b').
            prompt (str): The prompt text to send to the model.

        Returns:
            str: The raw stdout combined with stderr (if any) from the model execution.
        """
        p = subprocess.Popen(
            ["ollama", "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        out, err = p.communicate(prompt)

        return out + ("\n" + err if err else "")