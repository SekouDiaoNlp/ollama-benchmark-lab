import json
from pathlib import Path

STATE_FILE = Path("results/state.jsonl")


def write_state(obj: dict):
    STATE_FILE.parent.mkdir(exist_ok=True)
    with open(STATE_FILE, "a") as f:
        f.write(json.dumps(obj) + "\n")


def load_done():
    if not STATE_FILE.exists():
        return set()

    done = set()
    for line in STATE_FILE.read_text().splitlines():
        r = json.loads(line)
        if r.get("status") == "done":
            done.add((r["model"], r["task_id"]))
    return done