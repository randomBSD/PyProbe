"""Module entrypoint for running PyProbe as a package.

Usage: python -m pyprobe
"""
from .cli import main


def run() -> None:
    """Run the CLI main function."""
    main()


if __name__ == "__main__":
    run()
