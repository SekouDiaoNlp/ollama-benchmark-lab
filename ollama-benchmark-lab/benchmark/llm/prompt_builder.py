def build_patch_prompt(task: dict, repo_excerpt: str) -> str:
    return f"""
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
{task.get('task_id')}

REPO:
{task.get('repo_url')}
COMMIT:
{task.get('commit')}

TEST COMMAND:
{task.get('execution', {}).get('entrypoint', 'pytest -q')}

FILE CONTEXT (VERBATIM):
{repo_excerpt}

OUTPUT FORMAT:
diff --git a/<file> b/<file>
"""