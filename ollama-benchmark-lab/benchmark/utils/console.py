# benchmark/utils/console.py

class Console:
    """
    Simple colored console logger for CLI visibility.
    """

    RESET = "\033[0m"
    WHITE = "\033[97m"
    GREEN = "\033[92m"
    ORANGE = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"

    def info(self, msg: str):
        print(f"{self.WHITE}{msg}{self.RESET}")

    def success(self, msg: str):
        print(f"{self.GREEN}✔ {msg}{self.RESET}")

    def warn(self, msg: str):
        print(f"{self.ORANGE}⚠ {msg}{self.RESET}")

    def error(self, msg: str):
        print(f"{self.RED}✖ {msg}{self.RESET}")

    def step(self, msg: str):
        print(f"{self.GRAY}→ {msg}{self.RESET}")