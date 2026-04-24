"""
Unit tests for the OllamaClient.
"""

import pytest
from unittest.mock import MagicMock
from benchmark.ollama_client import OllamaClient

def test_ollama_run_success(mocker):
    """Test successful model execution."""
    mock_popen = mocker.patch("subprocess.Popen")
    mock_instance = mock_popen.return_value
    mock_instance.communicate.return_value = ("output text", "")
    
    client = OllamaClient()
    result = client.run("model-x", "hello")
    
    assert result == "output text"
    mock_popen.assert_called_once()
    args = mock_popen.call_args[0][0]
    assert "ollama" in args
    assert "run" in args
    assert "model-x" in args

def test_ollama_run_with_error(mocker):
    """Test model execution with stderr output."""
    mock_popen = mocker.patch("subprocess.Popen")
    mock_instance = mock_popen.return_value
    mock_instance.communicate.return_value = ("partial out", "error details")
    
    client = OllamaClient()
    result = client.run("model-x", "hello")
    
    assert "partial out" in result
    assert "error details" in result
