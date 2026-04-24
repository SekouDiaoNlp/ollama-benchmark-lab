"""
Unified Inference Engine for local LLM execution.

This module provides an abstraction layer over different local LLM backends
(Ollama, vLLM, etc.), ensuring a consistent API for the benchmark runner.
"""

from abc import ABC, abstractmethod
import subprocess
from typing import Optional
from benchmark.utils.console import Console


class BaseInferenceEngine(ABC):
    """
    Abstract base class for all local inference engines.
    """

    @abstractmethod
    def generate(self, model: str, prompt: str) -> str:
        """
        Execute a prompt against the local model.

        Args:
            model (str): The identifier for the local model.
            prompt (str): The input prompt for the model.

        Returns:
            str: The generated output text.
        """
        pass


class OllamaEngine(BaseInferenceEngine):
    """
    Inference engine implementation for the Ollama CLI.
    """

    def __init__(self) -> None:
        self.console: Console = Console()

    def generate(self, model: str, prompt: str) -> str:
        """
        Run inference using the Ollama CLI.

        Args:
            model (str): The Ollama model name (e.g., 'llama3').
            prompt (str): The input prompt.

        Returns:
            str: Combined stdout and stderr from the model.
        
        Raises:
            RuntimeError: If the Ollama process fails.
            FileNotFoundError: If the 'ollama' binary is not found.
        """
        try:
            # Use subprocess.run for cleaner handling of return codes and output
            proc = subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                text=True,
                capture_output=True,
                check=False
            )

            if proc.returncode != 0:
                error_msg = proc.stderr.strip() or "Unknown error"
                self.console.error(f"Ollama error: {error_msg}")
                raise RuntimeError(f"Ollama inference failed: {error_msg}")

            output = proc.stdout.strip()
            if not output:
                self.console.warn("Received empty response from Ollama")

            return output

        except FileNotFoundError:
            self.console.error("Ollama binary not found in system PATH")
            raise
