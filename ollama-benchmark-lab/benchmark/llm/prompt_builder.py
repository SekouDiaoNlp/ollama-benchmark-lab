"""
Strict SWE-bench prompting logic.

This module constructs the exact system prompts and instruction blocks
sent to the local Ollama instances to extract clean unified git diffs.

Example:
    >>> prompt = build_patch_prompt({"task_id": "1"}, "def test(): pass")
"""

from typing import Any, Dict


def build_patch_prompt(task: Dict[str, Any], repo_excerpt: str) -> str:
    """
    Build a dense instruction prompt tailored for patch generation.

    Args:
        task (Dict[str, Any]): The benchmark task payload.
        repo_excerpt (str): The truncated file context extracted from the repository.

    Returns:
        str: The complete formatted prompt text.
    """
    task_id: str = str(task.get('task_id', 'unknown'))
    repo_url: str = str(task.get('repo_url', 'unknown'))
    commit: str = str(task.get('commit', 'HEAD'))
    
    execution: Dict[str, Any] = task.get('execution', {})
    entrypoint: str = str(execution.get('entrypoint', 'pytest -q'))

    return f'''
You are a senior software engineer.

You MUST generate a valid git unified diff.

STRICT RULES:
- MUST apply cleanly with `git apply`
- MUST include exact original context lines
- DO NOT guess code
- DO NOT hallucinate files
- ONLY modify existing lines
- KEEP hunks small and precise

TASK:
{task_id}

REPO:
{repo_url}
COMMIT:
{commit}

TEST COMMAND:
{entrypoint}

FILE CONTEXT (VERBATIM):
{repo_excerpt}

OUTPUT FORMAT:
diff --git a/<file> b/<file>
'''