"""
Pydantic models for benchmark task validation.

This module defines the structured data models for ACT, PLAN, and SWE tasks,
ensuring strict type safety and schema compliance across the evaluation harness.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class TaskMode(str, Enum):
    """Supported task evaluation modes."""
    ACT = "ACT"
    PLAN = "PLAN"
    SWE = "SWE"


class TaskTests(BaseModel):
    """Configuration for task-specific tests."""
    model_config = ConfigDict(extra="ignore")
    
    path: str = Field(..., description="Path to the test file or directory")


class TaskExecution(BaseModel):
    """Configuration for task execution environment."""
    model_config = ConfigDict(extra="ignore")
    
    entrypoint: str = Field(..., description="Command to execute the task/tests")
    timeout: int = Field(default=300, description="Execution timeout in seconds")


class TaskRubric(BaseModel):
    """Optional evaluation rubric for grading."""
    model_config = ConfigDict(extra="ignore")
    
    correctness: Optional[float] = None
    structure: Optional[float] = None
    edge_cases: Optional[float] = None
    efficiency: Optional[float] = None


class BaseTask(BaseModel):
    """Base model for all benchmark tasks."""
    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="Unique task identifier")
    mode: TaskMode = Field(..., description="Evaluation mode (ACT, PLAN, SWE)")
    version: str = Field(..., description="Task schema version")
    public_prompt: str = Field(..., description="The prompt shown to the model")
    
    # Optional but common fields
    tests: Optional[TaskTests] = None
    execution: Optional[TaskExecution] = None
    rubric: Optional[TaskRubric] = None
    
    # SWE-specific but moved to base for flexibility in mixed tasks
    repo: Optional[str] = None
    base_commit: Optional[str] = None


class SWETask(BaseTask):
    """Strict model for SWE-bench tasks requiring repository context."""
    mode: TaskMode = TaskMode.SWE
    repo: str = Field(..., description="Repository name or URL")
    base_commit: str = Field(..., description="The git commit hash to checkout")
    execution: TaskExecution = Field(..., description="Execution block is required for SWE")


class PlanTask(BaseTask):
    """Model for planning-heavy tasks."""
    mode: TaskMode = TaskMode.PLAN


class ActTask(BaseTask):
    """Model for action-oriented tasks."""
    mode: TaskMode = TaskMode.ACT
