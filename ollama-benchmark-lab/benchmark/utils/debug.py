from pathlib import Path
import traceback


def debug_path(name, value):
    """
    Logs type + value + stack trace when things go wrong.
    Safe to leave in temporarily.
    """
    print("\n" + "=" * 80)
    print(f"[DEBUG PATH] {name}")
    print(f"TYPE: {type(value)}")
    print(f"VALUE: {value}")

    # highlight the bug early
    if isinstance(value, str):
        print("⚠️ WARNING: VALUE IS STRING (expected Path)")

    print("STACK TRACE:")
    traceback.print_stack(limit=8)
    print("=" * 80 + "\n")


def ensure_path(value, name="unknown"):
    """
    Forces Path conversion AND logs if conversion is needed.
    """
    if isinstance(value, str):
        debug_path(name, value)
        return Path(value)

    return value