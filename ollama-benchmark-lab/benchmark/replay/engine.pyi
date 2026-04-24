from _typeshed import Incomplete
from benchmark.replay.docker_runner import DockerRunner as DockerRunner
from benchmark.replay.patcher import apply_patch as apply_patch
from benchmark.replay.repo_manager import RepoManager as RepoManager

class ReplayEngine:
    repos: Incomplete
    runner: Incomplete
    def __init__(self) -> None: ...
    def run_task(self, task): ...
