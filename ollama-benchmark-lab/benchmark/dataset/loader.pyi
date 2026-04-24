from _typeshed import Incomplete

TASKS_DIR: Incomplete

class TaskLoader:
    def load_all(self) -> list[dict]: ...
    def load_by_id(self, task_id: str): ...
