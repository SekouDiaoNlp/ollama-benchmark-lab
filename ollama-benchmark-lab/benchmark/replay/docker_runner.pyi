IMAGE: str

class DockerRunner:
    def run_tests(self, repo_path, cmd: str = 'pytest -q', timeout: int = 120): ...
