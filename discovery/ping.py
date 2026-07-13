"""Ping-based discovery utilities.

This module provides a practical `ping_discover` implementation that tries
to use `scapy` when available and otherwise falls back to invoking the
platform `ping` command. The function performs a threaded sweep of the
specified CIDR and returns responding hosts.
"""
from __future__ import annotations

import subprocess
import sys
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List


def _ping_with_scapy(ip: str, timeout: float) -> bool:
    try:
        import scapy.all as scapy  # type: ignore
    except Exception:
        return False
    pkt = scapy.IP(dst=ip) / scapy.ICMP()
    resp = scapy.sr1(pkt, timeout=timeout, verbose=False)
    return resp is not None


def _ping_with_subprocess(ip: str, timeout: float) -> bool:
    # Use system ping. Windows uses '-n 1 -w <ms>' while Unix uses '-c 1 -W <s>' or '-W <ms>' on some systems
    if sys.platform.startswith("win"):
        cmd = ["ping", "-n", "1", "-w", str(int(timeout * 1000)), ip]
    else:
        # use -c 1 and -W in seconds (integer) where available; fall back to default timeout
        cmd = ["ping", "-c", "1", "-W", str(int(max(1, timeout))), ip]
    try:
        completed = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout + 1)
        return completed.returncode == 0
    except Exception:
        return False


def ping_discover(network: str, timeout: float = 1.0, workers: int = 100, max_hosts: int = 1024) -> List[str]:
    """Discover hosts by pinging all addresses in the given CIDR.

    Args:
        network: CIDR string like '192.168.1.0/24' or a single IP.
        timeout: per-host timeout in seconds.
        workers: number of threads for concurrent probes.
        max_hosts: maximum number of hosts to probe to avoid accidental large sweeps.

    Returns:
        List of responsive IP addresses as strings.
    """
    net = ipaddress.ip_network(network, strict=False)
    hosts = list(net.hosts()) if net.num_addresses > 1 else [net.network_address]
    if len(hosts) > max_hosts:
        raise ValueError(f"CIDR contains too many hosts ({len(hosts)}), increase max_hosts to override")

    # choose method: scapy if available, otherwise subprocess ping
    use_scapy = False
    try:
        import scapy.all  # type: ignore
        use_scapy = True
    except Exception:
        use_scapy = False

    results: List[str] = []
    with ThreadPoolExecutor(max_workers=min(workers, len(hosts))) as ex:
        futures = {}
        for ip in hosts:
            ipstr = str(ip)
            if use_scapy:
                futures[ex.submit(_ping_with_scapy, ipstr, timeout)] = ipstr
            else:
                futures[ex.submit(_ping_with_subprocess, ipstr, timeout)] = ipstr

        for fut in as_completed(futures):
            ipstr = futures[fut]
            try:
                alive = fut.result()
            except Exception:
                alive = False
            if alive:
                results.append(ipstr)

    return results

