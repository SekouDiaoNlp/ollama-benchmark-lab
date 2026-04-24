from benchmark.platform.api import BenchmarkPlatform
from benchmark.dataset.versioning import DatasetVersionControl


def load_dataset():
    import json
    from pathlib import Path

    tasks = []
    for f in Path("tasks").rglob("*.json"):
        tasks.append(json.loads(f.read_text()))
    return tasks


def run_pipeline():
    platform = BenchmarkPlatform()
    dataset_ctrl = DatasetVersionControl()

    dataset = load_dataset()
    snapshot_id = dataset_ctrl.save_snapshot(dataset)

    print(f"\n📦 Dataset snapshot: {snapshot_id}")

    report = platform.run_experiment(
        {"model": "docker-parity"},
        dataset
    )

    print("\n🏁 AUTOLLAMA DOCKER EXECUTION COMPLETE")
    print(report)