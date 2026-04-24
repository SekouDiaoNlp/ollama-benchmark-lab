from _typeshed import Incomplete
from benchmark.runtime.repo_manager import RepoManager as RepoManager
from benchmark.sandbox.image_builder import ImageBuilder as ImageBuilder

class DockerRunner:
    repo_manager: Incomplete
    image_builder: Incomplete
    def __init__(self) -> None: ...
    def run(self, repo_path: str, command: str): ...
