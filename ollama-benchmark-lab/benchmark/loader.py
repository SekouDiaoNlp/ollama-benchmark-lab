from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any


class TaskLoader:

    def __init__(self, root: str = "tasks/swe"):
        self.root = Path(root)

    def load_all(self) -> List[Dict[str, Any]]:
        tasks = []

        for task_dir in sorted(self.root.glob("*")):
            if not task_dir.is_dir():
                continue

            meta_file = task_dir / "prompt.json"

            if not meta_file.exists():
                continue

            task = json.loads(meta_file.read_text())

            # attach hidden tests path (NOT exposed to model)
            test_file = task_dir / "tests" / "test_hidden.py"
            if test_file.exists():
                task["hidden_tests"] = test_file.read_text()

            tasks.append(task)

        return tasks