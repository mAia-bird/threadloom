#!/usr/bin/env python3
"""Threadloom launcher.

    python run.py          # first time: runs setup; afterwards: starts the bot
    python run.py setup     # force the setup wizard
    python run.py --help    # this message

Requires Python 3.9+ and nothing else — only the standard library.
"""
import sys

if sys.version_info < (3, 9):
    sys.exit("Threadloom needs Python 3.9 or newer.")


def main() -> None:
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    if arg in ("-h", "--help", "help"):
        print(__doc__)
        return
    from threadloom.__main__ import main as entry
    entry()


if __name__ == "__main__":
    main()
