from dataclasses import dataclass

@dataclass
class SandboxResult:
    passed: bool
    returncode: int
    stdout: str
    stderr: str
    timeout: bool

class SandboxRunner:
    def run_code_with_tests(self, code: str, test_code: str, timeout: int = 5) -> SandboxResult: ...
