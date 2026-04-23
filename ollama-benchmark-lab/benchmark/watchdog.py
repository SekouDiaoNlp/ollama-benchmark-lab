import time
from pathlib import Path


class Watchdog:

    def __init__(self, heartbeat_file: Path, timeout_s: int = 300):
        self.file = heartbeat_file
        self.timeout = timeout_s

    def is_hung(self) -> bool:

        if not self.file.exists():
            return True

        data = self.file.read_text().strip()
        if not data:
            return True

        last = float(data.split("timestamp")[-1].split(":")[1].split(",")[0])

        return (time.time() - last) > self.timeout