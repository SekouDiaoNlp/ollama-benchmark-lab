from benchmark.sandbox.docker_runner import DockerRunner
from benchmark.dataset.loader import load_task_by_id
from pathlib import Path


runner = DockerRunner()


def run_task(task_id: str):
    task = load_task_by_id(task_id)

    repo = task.get("repo", ".")
    entrypoint = task["execution"]["entrypoint"]

    tests_path = task["tests"]["path"]

    # Compose execution command
    command = f"""
    cd /workspace && 
    {entrypoint} {tests_path}
    """

    result = runner.run(repo, command)

    return {
        "task_id": task_id,
        "exit_code": result["exit_code"],
        "logs": result["logs"],
        "status": result["status"]
    }