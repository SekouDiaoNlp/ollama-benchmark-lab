from benchmark.runtime.executor import run_task
from benchmark.adversarial.generator import AdversarialTestGenerator
from benchmark.adversarial.patch_mutation import PatchMutationEngine
from benchmark.scoring.evaluator import SWEBenchEvaluator


generator = AdversarialTestGenerator()
mutator = PatchMutationEngine()
evaluator = SWEBenchEvaluator()


def run_research_task(task: dict):
    """
    SWE-bench research mode:
    - baseline execution
    - adversarial stress tests
    - patch mutation robustness
    - scoring
    """

    baseline = run_task(task)

    adversarial = generator.generate(
        repo_path=task["repo"],
        patch=task.get("patch")
    )

    mutated = mutator.mutate(task.get("patch", ""))

    score = evaluator.evaluate(baseline)

    return {
        "baseline": baseline,
        "adversarial_tests": adversarial,
        "mutated_patch": mutated,
        "score": score
    }