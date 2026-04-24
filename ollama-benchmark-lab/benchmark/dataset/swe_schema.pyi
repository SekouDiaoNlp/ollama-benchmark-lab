from dataclasses import dataclass

@dataclass
class SWETask:
    task_id: str
    repo_url: str
    commit: str
    entrypoint: str = ...
    def validate(self) -> None: ...
