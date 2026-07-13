"""ASCII banner and dependency checks for PyProbe.

This module provides a startup banner and a lightweight dependency
checker that informs the user about optional packages.
"""
from __future__ import annotations

import importlib
from typing import Dict
import os

try:
    import ctypes
except Exception:
    ctypes = None

ASCII_BANNER = r"""
██████╗ ██╗   ██╗██████╗ ██████╗ █████╗ █████╗ ███████╗
██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
██████╔╝ ╚████╔╝ ██████╔╝██████╔╝██████╔╝██║   ██║██████╔╝
██╔═══╝   ╚██╔╝  ██╔═══╝ ██╔══██╗██╔══██╗██║   ██║██╔══██╗
██║        ██║   ██║     ██║  ██║██████╔╝╚██████╔╝██████╔╝
╚═╝        ╚═╝   ╚═╝     ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚══════╝

Python Network Discovery & Diagnostics Toolkit
"""


def check_dependencies(packages: Dict[str, str] | None = None) -> Dict[str, bool]:
    """Check whether a set of optional packages are importable.

    Prefer attempting to import the exact module name so nested packages
    (e.g. `scapy.all`) are detected more reliably.
    """
    if packages is None:
        packages = {"requests": "requests", "scapy.all": "scapy", "rich": "rich"}

    results: Dict[str, bool] = {}
    for import_name, label in packages.items():
        try:
            importlib.import_module(import_name)
            available = True
        except Exception:
            available = False
        results[label] = available
    return results


def scapy_privilege_status() -> Dict[str, bool]:
    """Return whether scapy is installed and whether we appear privileged.

    Returns a dict with keys `installed` and `privileged`.
    """
    installed = False
    privileged = False
    try:
        import scapy.all  # type: ignore

        installed = True
    except Exception:
        return {"installed": False, "privileged": False}

    # Check privilege: on Unix, UID 0; on Windows, attempt IsUserAnAdmin
    try:
        if os.name == "posix":
            privileged = (os.geteuid() == 0)
        elif os.name == "nt" and ctypes is not None:
            try:
                privileged = bool(ctypes.windll.shell32.IsUserAnAdmin())
            except Exception:
                privileged = False
        else:
            privileged = False
    except Exception:
        privileged = False

    return {"installed": installed, "privileged": privileged}


def show_banner(version: str | None = None) -> None:
    """Print the ASCII banner and basic version/dependency info.

    This function is intentionally side-effecting and prints to stdout.
    """
    print(ASCII_BANNER)
    if version:
        print(f"Version: {version}\n")
    print("[INFO] Checking dependencies...")
    deps = check_dependencies()
    missing = [name for name, avail in deps.items() if not avail]
    if not missing:
        print("[ OK ] All optional packages are available.")
    else:
        for name, available in deps.items():
            print(f"[{'OK' if available else '!!'}] {name}: {'OK' if available else 'MISSING'}")
        print()
        print("Optional packages missing: ", ", ".join(missing))
        print("Install them with: pip install -r requirements.txt")

    scapy_status = scapy_privilege_status()
    if scapy_status.get("installed"):
        if scapy_status.get("privileged"):
            print("[ OK ] scapy installed and running with privileges (raw sockets available).")
        else:
            print("[!!] scapy installed but not running with elevated privileges; some scans will be limited.")
            print("     Run as root/Administrator for full functionality (e.g. sudo python -m pyprobe ...)")
    else:
        # already covered in missing packages, but be explicit
        print("[!!] scapy not installed; privileged packet operations disabled.")
    print()
