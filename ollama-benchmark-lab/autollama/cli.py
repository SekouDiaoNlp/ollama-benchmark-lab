import argparse
from benchmark.platform.api import BenchmarkPlatform


def main():
    parser = argparse.ArgumentParser(prog="autollama")

    parser.add_argument("command", choices=["run"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--parallel", type=int, default=1)
    parser.add_argument("--model", type=str, default="default")

    args = parser.parse_args()

    if args.command == "run":
        config = {
            "model": args.model,
            "limit": args.limit,
            "parallel": args.parallel,
        }

        tasks = []  # placeholder until task loader is wired

        platform = BenchmarkPlatform(config=config)

        result = platform.run_experiment(config, tasks)

        print(result)