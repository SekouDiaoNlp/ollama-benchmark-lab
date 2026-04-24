from benchmark.runtime.repo_snapshot import RepoSnapshot
from benchmark.runtime.patch_engine import PatchEngine
from benchmark.sandbox.docker_runner import DockerRunner


repo_snapshot = RepoSnapshot()
patch_engine = PatchEngine()
docker = DockerRunner()


def run_task(task: dict):
    """
    SWE-bench parity execution pipeline.
    """

    repo = repo_snapshot.get(
        task["repo"],
        task["base_commit"]
    )

    if task.get("patch"):
        patch_engine.apply(repo, task["patch"])

    result = docker.run(
        repo_path=repo,
        command=task["execution"]["entrypoint"]
    )

    return {
        "id": task["id"],
        "tests_path": task["tests"]["path"],
        "entrypoint": task["execution"]["entrypoint"],
        "result": result
    }