import subprocess
import json
from benchmark.utils.console import Console


class LLMClient:
    """
    LOCAL-ONLY Ollama client.

    IMPORTANT:
    - No OpenAI / remote APIs allowed
    - Only local ollama models
    - Optimized for fastest iteration model
    """

    def __init__(self):
        self.console = Console()

        # FASTEST MODEL (based on benchmark results provided)
        self.model = "codegemma:2b-acting-noyap"

    def generate_patch(self, prompt: str) -> str:
        """
        Generate patch using local Ollama.
        """

        self.console.step(f"Using local model: {self.model}")

        try:
            proc = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt,
                text=True,
                capture_output=True,
            )

            if proc.returncode != 0:
                self.console.error(proc.stderr)
                raise RuntimeError("Ollama generation failed")

            output = proc.stdout.strip()

            if not output:
                self.console.warn("Empty response from model")

            return output

        except FileNotFoundError:
            self.console.error("Ollama is not installed or not in PATH")
            raise