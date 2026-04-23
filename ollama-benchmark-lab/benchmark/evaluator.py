import ast
import subprocess
import tempfile


def ast_valid(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except:
        return False


def run_code(code: str) -> bool:
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code)
            path = f.name

        r = subprocess.run(["python", path], capture_output=True, timeout=5)
        return r.returncode == 0
    except:
        return False


def style_score(code: str) -> float:
    score = 0.0
    score += 0.3 if "def" in code else 0
    score += 0.3 if "->" in code else 0
    score += 0.4 if len(code.splitlines()) > 5 else 0
    return score


def complexity_score(code: str) -> float:
    score = 1.0
    score -= code.count("for") * 0.2
    score -= code.count("while") * 0.2
    return max(0.0, score)