import time
import os

HB = "results/heartbeat.txt"


def heartbeat():
    with open(HB, "w") as f:
        f.write(str(time.time()))


def stale(threshold=300):
    if not os.path.exists(HB):
        return True

    last = float(open(HB).read())
    return (time.time() - last) > threshold