#!/usr/bin/env python3

import subprocess
import hashlib
import json
import time
import os
from collections import defaultdict, namedtuple

CACHE_DIR = ".cache_router"
METRICS_FILE = "router_metrics.json"

os.makedirs(CACHE_DIR, exist_ok=True)

Model = namedtuple("Model", ["name", "base", "tags"])


# =========================
# MODEL DISCOVERY
# =========================

def get_models():
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")[1:]
    return [line.split()[0] for line in lines if line.strip()]


# =========================
# SMART MODEL PARSING (FIXED)
# =========================

def parse_model(model_name):
    """
    Supports:
      qwen2.5:7b:planning-noyap
      qwen2.5:7b-planning-noyap
      codellama:7b-instruct:acting-noyap
    """

    # split ONLY first two segments as base (important fix)
    parts = model_name.split(":")

    if len(parts) < 3:
        return Model(model_name, model_name, set())

    base = ":".join(parts[:2])
    tag_part = ":".join(parts[2:])

    # normalize both formats:
    tag_part = tag_part.replace(":", "-")
    tags = set(tag_part.split("-"))

    return Model(model_name, base, tags)


# =========================
# GROUP MODELS
# =========================

def group_models(models):
    grouped = defaultdict(list)

    for m in models:
        parsed = parse_model(m)
        grouped[parsed.base].append(parsed)

    return grouped


# =========================
# TASK DETECTION (UPGRADED)
# =========================

def detect_task(prompt):
    p = prompt.lower()

    planning_signals = [
        "design", "architecture", "plan", "system",
        "strategy", "explain", "analyze", "why"
    ]

    acting_signals = [
        "implement", "code", "write", "refactor",
        "fix", "debug", "generate", "build"
    ]

    if any(k in p for k in planning_signals):
        return "planning"

    if any(k in p for k in acting_signals):
        return "acting"

    return "general"


# =========================
# SCORING ENGINE (NEW)
# =========================

def score_model(model: Model, task):
    score = 0
    tags = model.tags

    # base usefulness
    if "noyap" in tags:
        score += 2

    # direct task match
    if task in tags:
        score += 5

    # mismatch penalties (important)
    if task == "planning" and "acting" in tags:
        score -= 2

    if task == "acting" and "planning" in tags:
        score -= 2

    # general fallback preference
    if task == "general" and "planning" not in tags and "acting" not in tags:
        score += 1

    return score


# =========================
# FALLBACK CHAIN (NEW)
# =========================

def build_fallback_chain(models, task):
    """
    Priority:
    1. exact task match
    2. noyap general
    3. any base model
    """

    ranked = sorted(
        models,
        key=lambda m: score_model(m, task),
        reverse=True
    )

    return ranked


# =========================
# MODEL SELECTION (UPGRADED CORE)
# =========================

def select_model(prompt, models):
    task = detect_task(prompt)
    grouped = group_models(models)

    candidates = []

    for base, variants in grouped.items():
        candidates.extend(variants)

    ranked = build_fallback_chain(candidates, task)

    best = ranked[0] if ranked else None

    return best.name if best else None, task


# =========================
# CACHE
# =========================

def cache_key(prompt):
    return hashlib.sha256(prompt.encode()).hexdigest()


def get_cache(prompt):
    key = cache_key(prompt)
    path = os.path.join(CACHE_DIR, key)

    if os.path.exists(path):
        with open(path) as f:
            return f.read()

    return None


def set_cache(prompt, output):
    key = cache_key(prompt)
    path = os.path.join(CACHE_DIR, key)

    with open(path, "w") as f:
        f.write(output)


# =========================
# METRICS
# =========================

def record_metrics(model, duration):
    data = {}

    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE) as f:
            data = json.load(f)

    if model not in data:
        data[model] = {"calls": 0, "time": 0}

    data[model]["calls"] += 1
    data[model]["time"] += duration

    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# EXECUTION
# =========================

def run_model(model, prompt):
    start = time.time()

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        text=True,
        capture_output=True
    )

    record_metrics(model, time.time() - start)

    return result.stdout


# =========================
# ROUTER CORE
# =========================

def route(prompt):
    cached = get_cache(prompt)
    if cached:
        return cached

    models = get_models()
    model, task = select_model(prompt, models)

    print(f"[router] task={task} model={model}", flush=True)

    output = run_model(model, prompt)

    set_cache(prompt, output)
    return output


# =========================
# CLI ENTRY
# =========================

if __name__ == "__main__":
    import sys

    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("> ")
    print(route(prompt))
