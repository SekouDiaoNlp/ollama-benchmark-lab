from _typeshed import Incomplete
from benchmark.patch.engine import PatchEngine as PatchEngine

class DockerRunnerV2:
    patch_engine: Incomplete
    def __init__(self, patch_engine=None) -> None: ...
    def run(self, task): ...
