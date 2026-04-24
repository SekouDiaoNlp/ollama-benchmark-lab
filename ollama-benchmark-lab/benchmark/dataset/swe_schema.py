from dataclasses import dataclass


@dataclass
class SWETask:
    task_id: str
    repo_url: str
    commit: str

    entrypoint: str = "pytest -q"

    def validate(self):
        assert self.repo_url.startswith("https://")
        assert len(self.commit) >= 6