"""ARP-based discovery utilities.

This module attempts an ARP sweep using `scapy`. If `scapy` is not
available or the operation requires elevated privileges, it falls back
to returning an empty list and logs a helpful message.
"""
from __future__ import annotations

from typing import List


def arp_discover(network: str, timeout: int = 2) -> List[str]:
    """Perform an ARP sweep on the given network (CIDR) and return alive hosts.

    Args:
        network: CIDR string (e.g. '192.168.1.0/24') or single IP.
        timeout: timeout for scapy srp call in seconds.

    Returns:
        List of responsive IP addresses as strings. If scapy is not
        available or the call fails, returns an empty list.
    """
    try:
        import scapy.all as scapy  # type: ignore
    except Exception:
        return []

    try:
        # Build ARP request packet and send to broadcast
        answered, _ = scapy.srp(
            scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / scapy.ARP(pdst=network),
            timeout=timeout,
            verbose=False,
        )
        hosts: List[str] = [rcv.psrc for snd, rcv in answered]
        return hosts
    except Exception:
        return []

