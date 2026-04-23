import subprocess


class OllamaClient:

    def run(self, model: str, prompt: str) -> str:

        p = subprocess.Popen(
            ["ollama", "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        out, err = p.communicate(prompt)

        return out + ("\n" + err if err else "")