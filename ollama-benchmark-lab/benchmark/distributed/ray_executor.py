"""
Ray initialization and management for distributed execution.

This module provides utility functions to securely initialize a headless
Ray cluster for background task processing.
"""

import ray
import os

def init_ray() -> None:
    """
    Initialize Ray in headless mode with dashboard and usage stats disabled.
    """
    os.environ["RAY_DISABLE_DASHBOARD"] = "1"
    os.environ["RAY_USAGE_STATS_ENABLED"] = "0"

    ray.init(
        include_dashboard=False,
        ignore_reinit_error=True,
        logging_level="ERROR"
    )

def shutdown_ray() -> None:
    """
    Shutdown the current Ray session.
    """
    ray.shutdown()

if __name__ == "__main__":
    init_ray()
    print("ray ok (headless mode)")
    shutdown_ray()