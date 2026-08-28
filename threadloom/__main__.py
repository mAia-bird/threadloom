"""``python -m threadloom`` — same behavior as ``python run.py``."""
import sys

from .config import Config


def main() -> None:
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    if arg in ("setup", "--setup", "-s"):
        from .setup_wizard import main as setup_main
        setup_main()
        return
    if not Config().configured:
        # First run: nothing configured yet — walk the user through setup.
        from .setup_wizard import main as setup_main
        setup_main()
        return
    from .bot import run
    run()


if __name__ == "__main__":
    main()
