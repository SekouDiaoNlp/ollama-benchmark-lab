import ast


class SimpleEvaluator:

    def score(self, task, output: str) -> float:

        # heuristic scoring (upgrade later to AST + tests)
        score = 0.0

        if "def " in output:
            score += 0.4

        if "return" in output:
            score += 0.2

        if "test" in output.lower():
            score += 0.2

        try:
            ast.parse(output)
            score += 0.2
        except:
            pass

        return min(score, 1.0)