"""Port scanning helper that delegates to TCP scanners."""
from __future__ import annotations

from typing import List, Dict


def scan_ports(host: str, ports: List[int], timeout: float = 1.0, use_async: bool = False) -> Dict[int, bool]:
    """Scan ports on a host. Delegates to `tcp_scan` or `async_tcp_scan`.

    Args:
        host: target host
        ports: list of ports
        timeout: per-port timeout
        use_async: whether to use the asyncio scanner

    Returns:
        Mapping port -> bool
    """
    if not ports:
        return {}

    if use_async:
        try:
            import asyncio
            from .tcp_async import async_tcp_scan

            results = asyncio.run(async_tcp_scan(host, ports, timeout=timeout))
            return results
        except Exception:
            # fallback to sync scanner
            from .tcp import tcp_scan

            return tcp_scan(host, ports, timeout=timeout)

    # default: synchronous tcp_scan
    from .tcp import tcp_scan

    return tcp_scan(host, ports, timeout=timeout)

