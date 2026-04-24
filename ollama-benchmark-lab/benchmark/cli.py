import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

def main():
    import argparse
    from benchmark.platform import BenchmarkPlatform

    parser = argparse.ArgumentParser(prog="autollama")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("command", choices=["run"], help="Command to execute")

    args = parser.parse_args()

    if args.command == "run":
        platform = BenchmarkPlatform(limit=args.limit)
        platform.run_experiment()