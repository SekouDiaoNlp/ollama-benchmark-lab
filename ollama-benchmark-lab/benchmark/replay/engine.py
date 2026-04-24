from benchmark.replay.repo_manager import RepoManager
from benchmark.replay.patcher import apply_patch
from benchmark.replay.docker_runner import DockerRunner

class ReplayEngine:

    def __init__(self):
        self.repos = RepoManager()
        self.runner = DockerRunner()

    def run_task(self, task):
        repo = self.repos.get_repo(task["repo"])

        apply_patch(repo, task.get("patch", ""))

        result = self.runner.run_tests(
            repo,
            cmd=task["execution"]["entrypoint"]
        )

        return {
            "id": task["id"],
            "result": result
        }