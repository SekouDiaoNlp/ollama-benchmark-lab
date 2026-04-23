from pydantic import BaseModel
from typing import Optional, Dict


class TaskResult(BaseModel):
    model: str
    task_id: str
    mode: str

    success: bool
    duration: float

    ast_valid: bool
    runtime_pass: bool
    hidden_tests_pass: bool

    style_score: float
    complexity_score: float
    total_score: float

    error: Optional[str] = None
    metadata: Dict = {}