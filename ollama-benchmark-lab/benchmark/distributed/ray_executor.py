import ray
import os

def init_ray():
    os.environ["RAY_DISABLE_DASHBOARD"] = "1"
    os.environ["RAY_USAGE_STATS_ENABLED"] = "0"

    ray.init(
        include_dashboard=False,
        ignore_reinit_error=True,
        logging_level="ERROR"
    )

def shutdown_ray():
    ray.shutdown()


if __name__ == "__main__":
    init_ray()
    print("ray ok (headless mode)")
    shutdown_ray()