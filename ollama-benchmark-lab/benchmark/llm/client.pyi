from _typeshed import Incomplete
from benchmark.utils.console import Console as Console

class LLMClient:
    console: Incomplete
    model: str
    def __init__(self) -> None: ...
    def generate_patch(self, prompt: str) -> str: ...
