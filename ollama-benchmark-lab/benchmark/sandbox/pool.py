"""
Docker sandbox connection pooling.

This module provides a `SandboxPool` to manage pre-warmed Docker containers
for evaluating code executions in isolated environments safely.

Example:
    >>> pool = SandboxPool(size=2)
    >>> instance = pool.acquire()
    >>> output = instance.exec(["echo", "hello"])
    >>> pool.release(instance)
"""

import queue
from typing import Any, List, Optional

import docker  # type: ignore
from docker.models.containers import Container  # type: ignore
from docker.client import DockerClient  # type: ignore


IMAGE: str = "swe-sandbox:latest"
WORKDIR: str = "/workspace"


class SandboxInstance:
    """
    A single Docker container sandbox instance.

    Attributes:
        client (DockerClient): The Docker client instance.
        container (Container): The Docker container running sleep infinity.
        busy (bool): Whether the instance is currently executing a command.
    """

    def __init__(self, client: DockerClient, container: Container) -> None:
        """
        Initialize the SandboxInstance.

        Args:
            client (DockerClient): The active Docker API client.
            container (Container): The running Docker container.
        """
        self.client: DockerClient = client
        self.container: Container = container
        self.busy: bool = False

    def exec(self, cmd: List[str], timeout: int = 30) -> str:
        """
        Execute a command synchronously inside the running Docker container.

        Args:
            cmd (List[str]): The command to run as a list of strings.
            timeout (int): The execution timeout in seconds. Defaults to 30.

        Returns:
            str: The decoded standard output and standard error from the execution.
        """
        self.busy = True
        try:
            exec_id: Any = self.client.api.exec_create(
                self.container.id,
                cmd,
                workdir=WORKDIR,
                stdout=True,
                stderr=True,
            )

            output: bytes = self.client.api.exec_start(
                exec_id,
                stream=False
            )

            return output.decode("utf-8", errors="ignore")

        finally:
            self.busy = False


class SandboxPool:
    """
    A thread-safe pool of SandboxInstance containers.

    Attributes:
        client (DockerClient): The Docker API client.
        pool (queue.Queue[SandboxInstance]): The queue containing available instances.
    """

    def __init__(self, size: int = 4) -> None:
        """
        Initialize the SandboxPool and pre-warm containers.

        Args:
            size (int): The number of containers to keep in the pool. Defaults to 4.
        """
        self.client: DockerClient = docker.from_env()
        self.pool: "queue.Queue[SandboxInstance]" = queue.Queue()
        self._init_pool(size)

    def _init_pool(self, size: int) -> None:
        """
        Internal method to spawn and add the initial containers to the pool.

        Args:
            size (int): The number of containers to spawn.
        """
        for _ in range(size):
            container: Container = self.client.containers.run(
                IMAGE,
                command="sleep infinity",
                detach=True,
                tty=True,
                remove=True,
            )
            self.pool.put(SandboxInstance(self.client, container))

    def acquire(self, timeout: Optional[float] = None) -> SandboxInstance:
        """
        Acquire a SandboxInstance from the pool. Blocks if none are available.

        Args:
            timeout (Optional[float]): The maximum time to wait in seconds. Defaults to None.

        Returns:
            SandboxInstance: An available sandbox instance.

        Raises:
            queue.Empty: If a timeout is specified and no instance becomes available.
        """
        return self.pool.get(timeout=timeout)

    def release(self, instance: SandboxInstance) -> None:
        """
        Return a SandboxInstance back to the pool.

        Args:
            instance (SandboxInstance): The instance to release.
        """
        self.pool.put(instance)

    def close(self) -> None:
        """
        Clean up the pool by killing all running containers.
        """
        while not self.pool.empty():
            inst: SandboxInstance = self.pool.get()
            try:
                inst.container.kill()
            except Exception:
                pass