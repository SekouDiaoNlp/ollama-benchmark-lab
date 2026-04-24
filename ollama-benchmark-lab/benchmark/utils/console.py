"""
Utility console logger for benchmark execution visibility.

This module provides an instance-based Console class for printing formatted
status messages during the benchmark lifecycle.
"""

class Console:
    """
    Standard console output with predefined ANSI color formatting.

    Attributes:
        RESET (str): ANSI escape sequence to reset formatting.
        WHITE (str): ANSI escape sequence for white text.
        GREEN (str): ANSI escape sequence for green text.
        ORANGE (str): ANSI escape sequence for orange text.
        RED (str): ANSI escape sequence for red text.
        GRAY (str): ANSI escape sequence for gray text.
    """

    RESET: str = "\033[0m"
    WHITE: str = "\033[97m"
    GREEN: str = "\033[92m"
    ORANGE: str = "\033[93m"
    RED: str = "\033[91m"
    GRAY: str = "\033[90m"

    def info(self, msg: str) -> None:
        """
        Print an informational message in white.

        Args:
            msg (str): The info text.
        """
        print(f"{self.WHITE}{msg}{self.RESET}")

    def success(self, msg: str) -> None:
        """
        Print a success message with a checkmark.

        Args:
            msg (str): The success content.
        """
        print(f"{self.GREEN}✔ {msg}{self.RESET}")

    def warn(self, msg: str) -> None:
        """
        Print a warning message with an alert symbol.

        Args:
            msg (str): The warning details.
        """
        print(f"{self.ORANGE}⚠ {msg}{self.RESET}")

    def error(self, msg: str) -> None:
        """
        Print an error message with a cross symbol.

        Args:
            msg (str): The error content.
        """
        print(f"{self.RED}✖ {msg}{self.RESET}")

    def step(self, msg: str) -> None:
        """
        Print an execution step indicator in gray.

        Args:
            msg (str): The step description.
        """
        print(f"{self.GRAY}→ {msg}{self.RESET}")