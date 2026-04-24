"""
Minimal colored console output system.

This module provides the Console class for printing status messages with
standard ANSI color codes for terminal environments.
"""

class Console:
    """
    Standard terminal output with predefined color formatting.

    Attributes:
        GREEN (str): ANSI escape sequence for green text.
        ORANGE (str): ANSI escape sequence for orange text.
        RED (str): ANSI escape sequence for red text.
        WHITE (str): ANSI escape sequence for white text.
        RESET (str): ANSI escape sequence to reset formatting.
    """

    GREEN: str = "\033[92m"
    ORANGE: str = "\033[93m"
    RED: str = "\033[91m"
    WHITE: str = "\033[97m"
    RESET: str = "\033[0m"

    @staticmethod
    def ok(msg: str) -> None:
        """
        Print a success message with a checkmark.

        Args:
            msg (str): The message to display.
        """
        print(f"{Console.GREEN}✔ {msg}{Console.RESET}")

    @staticmethod
    def warn(msg: str) -> None:
        """
        Print a warning message with an alert symbol.

        Args:
            msg (str): The warning content.
        """
        print(f"{Console.ORANGE}⚠ {msg}{Console.RESET}")

    @staticmethod
    def error(msg: str) -> None:
        """
        Print an error message with a cross symbol.

        Args:
            msg (str): The error details.
        """
        print(f"{Console.RED}✖ {msg}{Console.RESET}")

    @staticmethod
    def info(msg: str) -> None:
        """
        Print an informational message in white.

        Args:
            msg (str): The info text.
        """
        print(f"{Console.WHITE}{msg}{Console.RESET}")