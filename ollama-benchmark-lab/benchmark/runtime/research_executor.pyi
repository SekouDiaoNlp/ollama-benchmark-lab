from _typeshed import Incomplete
from benchmark.adversarial.generator import AdversarialTestGenerator as AdversarialTestGenerator
from benchmark.adversarial.patch_mutation import PatchMutationEngine as PatchMutationEngine
from benchmark.runtime.executor import run_task as run_task
from benchmark.scoring.evaluator import SWEBenchEvaluator as SWEBenchEvaluator

generator: Incomplete
mutator: Incomplete
evaluator: Incomplete

def run_research_task(task: dict): ...
