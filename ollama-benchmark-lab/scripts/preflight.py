import os
import sys
import json
import subprocess
import time
from pathlib import Path

# =========================================================
# CRITICAL FIX: FORCE PROJECT ROOT ON IMPORT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ["PYTHONPATH"] = str(PROJECT_ROOT) + ":" + os.environ.get("PYTHONPATH", "")
sys.path.insert(0, str(PROJECT_ROOT))


CONFIG_PATH = PROJECT_ROOT / "benchmark_config.json"


# =========================================================
# CONFIG
# =========================================================

def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"safety": {"auto_repair": True}}


# =========================================================
# LOGGING
# =========================================================

def ok(msg: str):
    print(f"? {msg}", flush=True)


def warn(msg: str):
    print(f"? {msg}", flush=True)


def fail(msg: str):
    print(f"? {msg}", flush=True)


# =========================================================
# DIR CHECK
# =========================================================

def ensure_dir(path: Path, auto_repair: bool) -> bool:
    if path.exists():
        ok(f"Found: {path}")
        return True

    if auto_repair:
        warn(f"{path} missing → creating scaffold")
        path.mkdir(parents=True, exist_ok=True)
        ok(f"{path} created")
        return True

    fail(f"Missing directory: {path}")
    return False


# =========================================================
# TASKS
# =========================================================

def validate_tasks(auto_repair: bool) -> bool:
    base = PROJECT_ROOT / "tasks"

    if not base.exists():
        if auto_repair:
            warn("tasks/ missing → creating scaffold")
            for sub in ["plan", "act", "swe"]:
                (base / sub).mkdir(parents=True, exist_ok=True)
                ok(f"tasks/{sub}/ created")
            return True
        fail("tasks/ missing")
        return False

    for sub in ["plan", "act", "swe"]:
        ensure_dir(base / sub, auto_repair)

    files = list(base.glob("**/*.json"))
    ok(f"Tasks loaded: {len(files)} files")
    return True


# =========================================================
# OLLAMA
# =========================================================

def check_ollama():
    try:
        out = subprocess.check_output(["ollama", "list"], text=True)
        models = [l.strip() for l in out.splitlines() if l.strip()]
        ok(f"Ollama OK ({len(models)-1} models detected)")
        return True, models
    except Exception as e:
        fail(f"Ollama error: {e}")
        return False, []


# =========================================================
# DISK
# =========================================================

def check_writable():
    Path(PROJECT_ROOT / "results").mkdir(exist_ok=True)
    test = PROJECT_ROOT / "results/.write_test"
    test.write_text("ok")
    test.unlink()
    ok("Disk writable (results/)")
    return True


# =========================================================
# SMOKE MODEL SELECTION
# =========================================================

def select_smoke_models(models):
    def score(m):
        if "2b" in m:
            return 0
        if "3b" in m:
            return 1
        return 2

    return sorted(models, key=score)[:2]


# =========================================================
# SMOKE TEST
# =========================================================

def run_smoke_test(models):
    ok("\n=== SMOKE TEST START ===")

    try:
        from benchmark.runner import BenchmarkRunner
        from benchmark.ollama_client import OllamaClient
        from benchmark.checkpoint import CheckpointManager

        client = OllamaClient()
        ckpt = CheckpointManager(PROJECT_ROOT / "results/state.jsonl")
        runner = BenchmarkRunner(client, ckpt)

        task = {
            "id": "smoke_identity",
            "mode": "ACT",
            "prompt": "Return the string OK"
        }

        for m in models:
            ok(f"Running: {m}")

            res = runner.run_task(m, task)

            if not res.success:
                fail(f"Smoke failed: {m}")
                return False

            ok(f"{m} → score={res.score}")

        ok("=== SMOKE TEST PASSED ===")
        return True

    except Exception as e:
        fail(f"Smoke test crashed: {e}")
        return False


# =========================================================
# MAIN
# =========================================================

def main():
    cfg = load_config()
    auto_repair = cfg.get("safety", {}).get("auto_repair", True)

    print("\n=== PREFLIGHT CHECK (HARDENED MODE) ===\n")

    ok_state = True

    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}\n")

    ok_state &= ensure_dir(PROJECT_ROOT / "benchmark", auto_repair)
    ok_state &= ensure_dir(PROJECT_ROOT / "analysis", auto_repair)
    ok_state &= ensure_dir(PROJECT_ROOT / "dashboard", auto_repair)

    ok_state &= validate_tasks(auto_repair)

    ok_state &= check_writable()

    ollama_ok, models = check_ollama()
    ok_state &= ollama_ok

    if ok_state:
        smoke_models = select_smoke_models(models)

        print("\nSelected smoke models:")
        for m in smoke_models:
            print(" -", m)

        ok_state &= run_smoke_test(smoke_models)
    else:
        warn("Skipping smoke test due to system issues")

    print("\n==============================")
    if ok_state:
        ok("SYSTEM READY FOR BENCHMARK")
        sys.exit(0)
    else:
        fail("SYSTEM NOT READY")
        sys.exit(1)


if __name__ == "__main__":
    main()