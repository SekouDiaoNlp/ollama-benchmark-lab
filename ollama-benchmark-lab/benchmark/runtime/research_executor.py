"""
Advanced research execution runner for SWE-bench evaluations.

This module orchestrates baseline execution, adversarial test generation,
and patch mutation robustness analysis to rigorously score models.

Example:
    >>> from benchmark.runtime.research_executor import run_research_task
    >>> result = run_research_task({"id": "task1", "repo": "foo", "base_commit": "HEAD", "execution": {"entrypoint": "pytest"}})
"""

from typing import Any, Dict

from benchmark.runtime.executor import run_task
from benchmark.adversarial.generator import AdversarialTestGenerator
from benchmark.adversarial.patch_mutation import PatchMutationEngine
from benchmark.scoring.evaluator import SWEBenchEvaluator

# Initialize heavy engines once per process
generator = AdversarialTestGenerator()
mutator = PatchMutationEngine()
evaluator = SWEBenchEvaluator()


def run_research_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an SWE-bench task using the full research evaluation pipeline.

    This includes:
    - baseline execution
    - adversarial stress tests
    - patch mutation robustness
    - deep scoring

    Args:
        task (Dict[str, Any]): The benchmark task dictionary.

    Returns:
        Dict[str, Any]: A detailed report including baseline results, adversarial outputs,
            mutation metrics, and the final score.
    """
    baseline: Dict[str, Any] = run_task(task)

    adversarial: Any = generator.generate(
        repo_path=str(task["repo"]),
        patch=task.get("patch")
    )

    mutated: Any = mutator.mutate(task.get("patch", ""))

    score: float = evaluator.evaluate(baseline)

    return {
        "baseline": baseline,
        "adversarial_tests": adversarial,
        "mutated_patch": mutated,
        "score": score
    }