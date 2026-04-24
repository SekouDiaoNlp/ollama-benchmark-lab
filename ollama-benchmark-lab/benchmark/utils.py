from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "benchmark_config.json"


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"[CONFIG ERROR] Missing benchmark_config.json at {CONFIG_PATH}"
        )

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    validate_config(config)
    return config


def validate_config(cfg: Dict[str, Any]) -> None:
    required_sections = [
        "model_selection",
        "execution",
        "checkpointing",
        "scoring",
        "safety",
    ]

    for section in required_sections:
        if section not in cfg:
            raise ValueError(f"[CONFIG ERROR] Missing section: {section}")

    # enforce consistency rules
    if cfg["execution"]["parallel_models"] < 1:
        raise ValueError("parallel_models must be >= 1")

    if cfg["prompting"]["plan_ratio"] + cfg["prompting"]["act_ratio"] != 1:
        raise ValueError("plan_ratio + act_ratio must equal 1.0")