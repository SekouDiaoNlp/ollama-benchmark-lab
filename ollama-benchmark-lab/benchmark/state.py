import time
from pydantic import BaseModel


class JobState(BaseModel):
    model: str
    task_id: str
    status: str  # pending/running/done/failed
    started_at: float = time.time()
    last_heartbeat: float = time.time()
    retries: int = 0