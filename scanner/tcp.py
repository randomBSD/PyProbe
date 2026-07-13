"""TCP scanning helpers.

This module provides a threaded TCP connect scanner using `socket` and
`concurrent.futures.ThreadPoolExecutor`. It attempts to connect to each
port with a timeout and reports which ports accepted a TCP connection.
"""
from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List


def _check_port(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def tcp_scan(host: str, ports: List[int], timeout: float = 1.0, workers: int = 100) -> Dict[int, bool]:
    """Scan TCP ports by attempting TCP connect on each port.

    Args:
        host: target hostname or IP.
        ports: iterable of ports to scan.
        timeout: socket connect timeout in seconds.
        workers: number of threads to use.

    Returns:
        Mapping of port -> bool (True if open).
    """
    results: Dict[int, bool] = {}
    if not ports:
        return results

    with ThreadPoolExecutor(max_workers=min(workers, len(ports))) as ex:
        futures = {ex.submit(_check_port, host, p, timeout): p for p in ports}
        for fut in as_completed(futures):
            p = futures[fut]
            try:
                ok = fut.result()
            except Exception:
                ok = False
            results[p] = ok

    return results

