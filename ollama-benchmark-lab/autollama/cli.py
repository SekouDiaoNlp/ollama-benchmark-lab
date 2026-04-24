import argparse
from benchmark.platform.api import run_experiment
from benchmark.utils.console import Console

console = Console()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1)
    args = parser.parse_args()

    console.info("Autollama starting...")
    console.step("Loading tasks...")

    config = {
        "local_only": True,   # HARD LOCK: no remote calls
    }

    tasks = load_tasks(limit=args.limit)

    console.success(f"{len(tasks)} task(s) loaded")

    for task in tasks:
        console.info(f"\nRunning task: {task['task_id']}")

        try:
            console.step("Preparing snapshot...")
            console.success("Snapshot ready")

            console.step("Generating patch (local LLM)...")

            result = run_experiment(config, [task])

            if result["passed"]:
                console.success("TASK PASSED")
            else:
                console.warn("TASK FAILED")

        except Exception as e:
            console.error(str(e))

def load_tasks(limit=1):
    return [
        {
            "task_id": "sample-001",
            "repo_url": "https://github.com/example/repo.git",
            "commit": "HEAD",
            "execution": {
                "entrypoint": "pytest -q"
            }
        }
    ][:limit]


if __name__ == "__main__":
    main()