import argparse

from benchmark.platform.api import BenchmarkPlatform
from benchmark.dataset.swe_loader import SWEBenchLoader


def main():
    parser = argparse.ArgumentParser(prog="autollama")

    parser.add_argument("command", choices=["run"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model", type=str, default="default")

    args = parser.parse_args()

    if args.command == "run":
        loader = SWEBenchLoader()
        tasks = loader.load_all()

        if args.limit:
            tasks = tasks[: args.limit]

        config = {"model": args.model}

        platform = BenchmarkPlatform(config=config)

        result = platform.run_experiment(config, tasks)

        print(result)