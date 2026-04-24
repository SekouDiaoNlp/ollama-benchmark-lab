#!/usr/bin/env python3

import sys
from pathlib import Path

# =========================================================
# FIX IMPORT PATH (CRITICAL FOR POETRY + SCRIPTS)
# =========================================================

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# =========================================================
# IMPORTS
# =========================================================

import json
import subprocess

from benchmark.validation.schema_validator import SchemaValidator


# =========================================================
# CONFIG
# =========================================================

CONFIG_PATH = ROOT / "benchmark_config.json"


def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {
        "safety": {
            "auto_repair": True,
            "fail_fast": False
        }
    }


# =========================================================
# DIRECTORY CHECKS
# =========================================================

def ensure_dir(path: Path, auto_repair: bool):
    if not path.exists():
        if auto_repair:
            print(f"⚠ {path} missing → creating")
            path.mkdir(parents=True, exist_ok=True)
            print(f"✔ {path} created")
            return True
        else:
            print(f"✖ Missing directory: {path}")
            return False
    print(f"✔ Found: {path}")
    return True


# =========================================================
# SYSTEM CHECKS
# =========================================================

def check_ollama():
    try:
        out = subprocess.check_output(["ollama", "list"], text=True)
        lines = [l for l in out.splitlines() if l.strip()]
        count = len(lines) - 1  # skip header
        if count <= 0:
            print("✖ No models detected in ollama")
            return False
        print(f"✔ Ollama OK ({count} models detected)")
        return True
    except Exception as e:
        print(f"✖ Ollama not reachable: {e}")
        return False


def check_writable():
    try:
        results = ROOT / "results"
        results.mkdir(exist_ok=True)
        test = results / ".write_test"
        test.write_text("ok")
        test.unlink()
        print("✔ Disk writable (results/)")
        return True
    except Exception as e:
        print(f"✖ Write failure: {e}")
        return False


# =========================================================
# TASK VALIDATION
# =========================================================

def validate_tasks(auto_repair: bool):
    validator = SchemaValidator(auto_repair=auto_repair)

    tasks_dir = ROOT / "tasks"
    files = list(tasks_dir.glob("**/*.json"))

    total = len(files)
    valid = 0
    invalid = 0

    errors = {}

    for f in files:
        result = validator.validate_file(f)

        if result["valid"]:
            valid += 1
        else:
            invalid += 1
            errors[f.stem] = result["errors"]

    print("\n📦 SCHEMA VALIDATION")
    print(f"✔ Total: {total}")
    print(f"✔ Valid: {valid}")
    print(f"✖ Invalid: {invalid}")

    if errors:
        print("\n❌ STRUCTURED ERRORS:")
        for k, v in list(errors.items())[:10]:
            print(f" - {k}: {v}")

    return total, valid, invalid


# =========================================================
# GOLDEN TEST CHECK
# =========================================================

def check_golden_tasks():
    tasks_dir = ROOT / "tasks"
    files = list(tasks_dir.glob("**/*.json"))

    golden = 0

    for f in files:
        data = json.loads(f.read_text())
        if data.get("golden"):
            golden += 1

    print("\n🧪 GOLDEN TEST SUITE")
    print(f"✔ Golden tasks: {golden}")

    return golden


# =========================================================
# MAIN
# =========================================================

def main():
    cfg = load_config()

    auto_repair = cfg.get("safety", {}).get("auto_repair", True)
    fail_fast = cfg.get("safety", {}).get("fail_fast", False)

    print("\n=== PREFLIGHT (FULL VALIDATION MODE) ===\n")

    print(f"Python: {sys.version}")
    print(f"Exec: {sys.executable}")

    ok = True

    # -----------------------------------------------------
    # STRUCTURE
    # -----------------------------------------------------

    ok &= ensure_dir(ROOT / "benchmark", auto_repair)
    ok &= ensure_dir(ROOT / "analysis", auto_repair)
    ok &= ensure_dir(ROOT / "dashboard", auto_repair)
    ok &= ensure_dir(ROOT / "tasks/plan", auto_repair)
    ok &= ensure_dir(ROOT / "tasks/act", auto_repair)
    ok &= ensure_dir(ROOT / "tasks/swe", auto_repair)

    # -----------------------------------------------------
    # TASK VALIDATION
    # -----------------------------------------------------

    total, valid, invalid = validate_tasks(auto_repair)

    if fail_fast and invalid > 0:
        print("\n❌ STRICT MODE ENABLED → INVALID TASKS BLOCK EXECUTION")
        sys.exit(1)

    # -----------------------------------------------------
    # SYSTEM CHECKS
    # -----------------------------------------------------

    ok &= check_writable()
    ok &= check_ollama()

    # -----------------------------------------------------
    # GOLDEN TASKS
    # -----------------------------------------------------

    golden = check_golden_tasks()

    # -----------------------------------------------------
    # FINAL STATUS
    # -----------------------------------------------------

    print("\n==============================")
    print("📊 SYSTEM VALIDATION COMPLETE")
    print(f"Tasks:  {total}")
    print(f"Valid:  {valid}")
    print(f"Golden: {golden}")
    print("==============================")

    if ok:
        print("🚀 READY FOR BENCHMARK")
        sys.exit(0)
    else:
        print("❌ SYSTEM NOT READY")
        sys.exit(1)


if __name__ == "__main__":
    main()