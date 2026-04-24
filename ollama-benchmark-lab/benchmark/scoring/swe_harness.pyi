from _typeshed import Incomplete
from benchmark.sandbox.runner import SandboxRunner as SandboxRunner
from typing import Any

class SWEHarnessScorer:
    sandbox: Incomplete
    def __init__(self) -> None: ...
    def score(self, task: dict[str, Any], output: str) -> float: ...
