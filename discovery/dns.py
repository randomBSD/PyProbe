"""DNS utilities for discovery.

Provides a basic `dns_lookup` that prefers `dnspython` when available
but falls back to `socket.getaddrinfo`.
"""
from __future__ import annotations

import socket
from typing import List


def dns_lookup(name: str) -> List[str]:
    """Resolve a DNS name to one or more IP addresses.

    Args:
        name: hostname to resolve.

    Returns:
        List of IPv4/IPv6 addresses as strings. Empty list on failure.
    """
    # Try dnspython first for richer resolution
    try:
        import dns.resolver  # type: ignore

        answers = dns.resolver.resolve(name)
        results = [r.to_text() for r in answers]
        return results
    except Exception:
        pass

    # Fallback to socket.getaddrinfo
    try:
        infos = socket.getaddrinfo(name, None)
        addrs = []
        for info in infos:
            sockaddr = info[4]
            addr = sockaddr[0]
            if addr not in addrs:
                addrs.append(addr)
        return addrs
    except Exception:
        return []

