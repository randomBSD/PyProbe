"""
PyProbe entry point.

Allows the package to be executed with:

    python -m pyprobe
"""

from pyprobe.cli import main


def run() -> None:
    """Launch the PyProbe CLI."""
    main()


if __name__ == "__main__":
    run()
