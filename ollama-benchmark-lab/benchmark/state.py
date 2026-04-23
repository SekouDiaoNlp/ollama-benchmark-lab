import time
from pydantic import BaseModel


class JobState(BaseModel):
    model: str
    task_id: str
    status: str  # pending/running/done/failed
    started_at: float = time.time()
    last_heartbeat: float = time.time()
    retries: int = 0

class RunState:
    """
    Reserved for future:
    - distributed execution
    - remote worker sync
    - leaderboard updates
    """
    pass