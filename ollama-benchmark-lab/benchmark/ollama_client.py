import subprocess
import time


def run_ollama(model: str, prompt: str, timeout: int = 180):
    start = time.time()

    try:
        p = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return p.stdout.decode(), time.time() - start

    except subprocess.TimeoutExpired:
        return "", -1