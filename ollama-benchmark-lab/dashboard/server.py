from fastapi import FastAPI
import json

app = FastAPI()

FILE = "results/results.jsonl"


@app.get("/leaderboard")
def leaderboard():
    data = {}

    with open(FILE) as f:
        for line in f:
            r = json.loads(line)
            m = r["model"]
            data.setdefault(m, []).append(r["total_score"])

    return {m: sum(v)/len(v) for m, v in data.items()}