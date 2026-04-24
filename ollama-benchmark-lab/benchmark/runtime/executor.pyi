from _typeshed import Incomplete
from benchmark.runtime.patch_engine import PatchEngine as PatchEngine
from benchmark.runtime.repo_snapshot import RepoSnapshot as RepoSnapshot
from benchmark.sandbox.docker_runner_v2 import DockerRunnerV2 as DockerRunnerV2

repo_snapshot: Incomplete
patch_engine: Incomplete
docker: Incomplete

def run_task(task: dict): ...
