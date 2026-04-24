def main():
    import argparse
    from benchmark.platform import BenchmarkPlatform

    parser = argparse.ArgumentParser(prog="autollama")
    parser.add_argument("command", choices=["run"], help="Command to execute")

    args = parser.parse_args()

    if args.command == "run":
        platform = BenchmarkPlatform()
        platform.run_experiment()