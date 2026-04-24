import argparse
from benchmark.platform.api import BenchmarkPlatform
from benchmark.dataset.versioning import DatasetVersionControl


def load_dataset():
    # minimal placeholder loader (can be swapped with SWE-bench JSON loader)
    import json
    from pathlib import Path

    path = Path("tasks")
    tasks = []

    for f in path.rglob("*.json"):
        tasks.append(json.loads(f.read_text()))

    return tasks


def run_pipeline():
    platform = BenchmarkPlatform()
    dataset_ctrl = DatasetVersionControl()

    dataset = load_dataset()
    snapshot_id = dataset_ctrl.save_snapshot(dataset)

    print(f"\n📦 Dataset snapshot: {snapshot_id}")

    # mock execution results for now (hook into DockerRunner later)
    results = [
        {
            "task_id": t.get("id", "unknown"),
            "passed": True,
            "stderr": "",
        }
        for t in dataset
    ]

    config = {
        "model": "autollama-default",
        "snapshot": snapshot_id
    }

    report = platform.run_experiment(config, results)

    print("\n🏁 AUTOLLAMA RUN COMPLETE")
    print(report)


def main():
    parser = argparse.ArgumentParser(prog="autollama")
    parser.add_argument("command", choices=["run"])

    args = parser.parse_args()

    if args.command == "run":
        run_pipeline()


if __name__ == "__main__":
    main()