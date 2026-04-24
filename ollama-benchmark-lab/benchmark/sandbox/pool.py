import docker
import queue
from typing import Optional

IMAGE = "swe-sandbox:latest"
WORKDIR = "/workspace"


class SandboxInstance:
    def __init__(self, client, container):
        self.client = client
        self.container = container
        self.busy = False

    def exec(self, cmd, timeout=30):
        self.busy = True
        try:
            exec_id = self.client.api.exec_create(
                self.container.id,
                cmd,
                workdir=WORKDIR,
                stdout=True,
                stderr=True,
            )

            output = self.client.api.exec_start(
                exec_id,
                stream=False
            )

            return output.decode("utf-8", errors="ignore")

        finally:
            self.busy = False


class SandboxPool:
    def __init__(self, size=4):
        self.client = docker.from_env()
        self.pool = queue.Queue()
        self._init_pool(size)

    def _init_pool(self, size):
        for _ in range(size):
            container = self.client.containers.run(
                IMAGE,
                command="sleep infinity",
                detach=True,
                tty=True,
                remove=True,
            )
            self.pool.put(SandboxInstance(self.client, container))

    def acquire(self, timeout=None) -> SandboxInstance:
        return self.pool.get(timeout=timeout)

    def release(self, instance: SandboxInstance):
        self.pool.put(instance)

    def close(self):
        while not self.pool.empty():
            inst = self.pool.get()
            try:
                inst.container.kill()
            except Exception:
                pass