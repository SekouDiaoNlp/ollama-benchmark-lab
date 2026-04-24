from pathlib import Path

from benchmark.runtime.repo_snapshot import RepoSnapshot
from benchmark.runtime.patch_engine import PatchEngine
from benchmark.sandbox.docker_runner_v2 import DockerRunnerV2


repo_snapshot = RepoSnapshot()
patch_engine = PatchEngine()
docker = DockerRunnerV2()


def run_task(task: dict):

    print(f"[EXECUTOR DEBUG] TASK ID={task.get('id')}")

    repo = repo_snapshot.get(task["repo"], task["base_commit"])

    print(f"[EXECUTOR DEBUG] repo type={type(repo)} value={repo}")

    if repo is None:
        raise RuntimeError("Missing repo snapshot")

    if task.get("patch"):
        patch_engine.apply(repo, task["patch"])

    # 🔥 CRITICAL TRACE POINT
    print(f"[EXECUTOR DEBUG] BEFORE EXISTS CHECK type={type(repo)} value={repo}")

    repo_path = Path(repo)

    print(f"[EXECUTOR DEBUG] AFTER PATH WRAP type={type(repo_path)} value={repo_path}")

    if not repo_path.exists():
        print(f"[EXECUTOR DEBUG] INVALID PATH: {repo_path}")
        raise RuntimeError(f"Invalid repo path resolved: {repo}")

    result = docker.run(
        repo_path=repo_path,
        command=task["execution"]["entrypoint"]
    )

    return {
        "id": task["id"],
        "result": result
    }