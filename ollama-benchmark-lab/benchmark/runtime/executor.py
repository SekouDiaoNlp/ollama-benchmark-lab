from benchmark.runtime.repo_manager import RepoManager
from benchmark.runtime.patch_engine import PatchEngine
from benchmark.sandbox.docker_runner import DockerRunner


repo_manager = RepoManager()
patch_engine = PatchEngine()
docker = DockerRunner()


def run_task(task: dict):
    """
    Full SWE-bench execution pipeline.
    """

    repo = repo_manager.get_repo(
        task["repo"],
        task["base_commit"]
    )

    if "patch" in task:
        patch_engine.apply_patch(repo, task["patch"])

    result = docker.run(
        repo_path=repo,
        command=task["execution"]["entrypoint"]
    )

    return {
        "tests_path": task["tests"]["path"],
        "entrypoint": task["execution"]["entrypoint"],
        "result": result
    }