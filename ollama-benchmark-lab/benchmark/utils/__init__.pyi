from pathlib import Path
from typing import Any

def load_config(path: str | Path | dict[str, Any] = 'config.json') -> dict[str, Any]: ...
