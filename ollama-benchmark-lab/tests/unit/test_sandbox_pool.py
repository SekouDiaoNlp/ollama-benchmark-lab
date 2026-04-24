"""
Unit tests for the SandboxPool.
"""

import pytest
from unittest.mock import MagicMock
from benchmark.sandbox.pool import SandboxPool, SandboxInstance

def test_sandbox_pool_initialization(mocker):
    """Test pool pre-warming."""
    mock_docker = mocker.patch("docker.from_env")
    mock_client = mock_docker.return_value
    
    pool = SandboxPool(size=2)
    
    assert mock_client.containers.run.call_count == 2
    assert pool.pool.qsize() == 2

def test_sandbox_acquire_release(mocker):
    """Test acquiring and releasing instances."""
    mocker.patch("docker.from_env")
    pool = SandboxPool(size=1)
    
    instance = pool.acquire()
    assert isinstance(instance, SandboxInstance)
    assert pool.pool.empty()
    
    pool.release(instance)
    assert pool.pool.qsize() == 1

def test_sandbox_instance_exec(mocker):
    """Test command execution in a sandbox instance."""
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_container.id = "c123"
    
    # Mock exec_create and exec_start
    mock_client.api.exec_create.return_value = {"Id": "e123"}
    mock_client.api.exec_start.return_value = b"command output"
    
    instance = SandboxInstance(mock_client, mock_container)
    output = instance.exec(["ls", "-l"])
    
    assert output == "command output"
    mock_client.api.exec_create.assert_called_once()
    mock_client.api.exec_start.assert_called_once_with({"Id": "e123"}, stream=False)

def test_sandbox_pool_close(mocker):
    """Test cleaning up the pool."""
    mocker.patch("docker.from_env")
    pool = SandboxPool(size=2)
    
    inst1 = pool.pool.get()
    inst2 = pool.pool.get()
    
    inst1.container = MagicMock()
    inst2.container = MagicMock()
    
    pool.pool.put(inst1)
    pool.pool.put(inst2)
    
    pool.close()
    
    inst1.container.kill.assert_called_once()
    inst2.container.kill.assert_called_once()
