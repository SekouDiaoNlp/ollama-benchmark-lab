from _typeshed import Incomplete
from benchmark.sandbox.docker_runner import DockerSandboxRunner as DockerSandboxRunner
from typing import Any

class SWEBenchScorer:
    runner: Incomplete
    def __init__(self) -> None: ...
    def score(self, task: dict[str, Any], output: str) -> float: ...
