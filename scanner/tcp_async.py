"""Async TCP scanner using asyncio for high concurrency."""
from __future__ import annotations

import asyncio
from typing import Dict, Iterable, List


async def _check_port(host: str, port: int, timeout: float, sem: asyncio.Semaphore) -> (int, bool):
    async with sem:
        try:
            conn = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(conn, timeout=timeout)
            try:
                writer.close()
                if hasattr(writer, "wait_closed"):
                    await writer.wait_closed()
            except Exception:
                pass
            return port, True
        except Exception:
            return port, False


async def async_tcp_scan(host: str, ports: Iterable[int], timeout: float = 1.0, concurrency: int = 500) -> Dict[int, bool]:
    """Asynchronously scan TCP ports using asyncio.

    Args:
        host: target hostname or IP
        ports: iterable of ports to scan
        timeout: per-connection timeout in seconds
        concurrency: maximum number of simultaneous connection attempts

    Returns:
        Mapping port -> bool (True if open)
    """
    ports_list: List[int] = list(ports)
    sem = asyncio.Semaphore(concurrency)
    tasks = [asyncio.create_task(_check_port(host, p, timeout, sem)) for p in ports_list]
    results: Dict[int, bool] = {}
    for fut in asyncio.as_completed(tasks):
        p, ok = await fut
        results[p] = ok
    return results
