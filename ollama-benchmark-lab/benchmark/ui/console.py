class Console:
    """
    Minimal colored output system.
    """

    GREEN = "\033[92m"
    ORANGE = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    RESET = "\033[0m"

    @staticmethod
    def ok(msg: str):
        print(f"{Console.GREEN}✔ {msg}{Console.RESET}")

    @staticmethod
    def warn(msg: str):
        print(f"{Console.ORANGE}⚠ {msg}{Console.RESET}")

    @staticmethod
    def error(msg: str):
        print(f"{Console.RED}✖ {msg}{Console.RESET}")

    @staticmethod
    def info(msg: str):
        print(f"{Console.WHITE}{msg}{Console.RESET}")