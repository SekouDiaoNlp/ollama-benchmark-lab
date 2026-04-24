from benchmark.runtime.repo_manager import get_repo
from benchmark.runtime.patcher import apply_patch
from benchmark.sandbox.docker_runner import run_in_container


def run_task_instance(task: dict):
    """
    Core SWE-bench execution pipeline:
    repo → patch → docker → pytest
    """

    repo = get_repo(
        task["repo"],
        task["base_commit"]
    )

    apply_patch(repo, task["patch"])

    result = run_in_container(
        repo_path=repo,
        command="pytest -q"
    )

    return result