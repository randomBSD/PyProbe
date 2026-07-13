"""UDP scanning helpers with privileged ICMP handling when available.

This module will attempt to use `scapy` (if installed and running with
the required privileges) to detect ICMP "port unreachable" messages
that indicate closed UDP ports. When `scapy` is not available the
function falls back to a socket-based send/recv approach.

Return values:
    Mapping[int, str] where the string is one of:
      - 'open' : service responded with UDP data
      - 'closed' : ICMP port unreachable received (scapy path)
      - 'open|filtered' : no response (could be open or filtered)
      - 'error' : an error occurred performing the probe
"""
from __future__ import annotations

import socket
from typing import Dict, List


def udp_scan(host: str, ports: List[int], timeout: float = 1.0) -> Dict[int, str]:
    """Scan UDP ports and try to detect closed ports via ICMP unreachable.

    Args:
        host: target IP/hostname
        ports: list of UDP ports to probe
        timeout: per-port timeout in seconds

    Returns:
        Mapping port -> status string ('open', 'closed', 'open|filtered', 'error')
    """
    # Try scapy first for privileged ICMP detection
    try:
        import scapy.all as scapy  # type: ignore
    except Exception:
        scapy = None

    results: Dict[int, str] = {}

    if scapy is not None:
        # Build packets and send using scapy.sr to capture ICMP replies
        pkts = [scapy.IP(dst=host) / scapy.UDP(dport=p) / b"" for p in ports]
        try:
            answered, unanswered = scapy.sr(pkts, timeout=timeout, verbose=False)
            # Initialize as open|filtered
            for p in ports:
                results[p] = "open|filtered"

            # Process answered packets
            for snd, rcv in answered:
                # extract destination port from original packet
                try:
                    dport = int(snd[scapy.UDP].dport)
                except Exception:
                    continue

                # If we received ICMP type 3 code 3 -> port unreachable -> closed
                if rcv.haslayer(scapy.ICMP):
                    icmp = rcv.getlayer(scapy.ICMP)
                    if int(icmp.type) == 3 and int(icmp.code) == 3:
                        results[dport] = "closed"
                        continue

                # If we received a UDP payload back -> open
                if rcv.haslayer(scapy.UDP):
                    results[dport] = "open"
                    continue

            # Unanswered remain 'open|filtered'
            return results
        except PermissionError:
            # Likely not running with privileges to send/receive raw packets
            scapy = None
        except Exception:
            # On other failures, fall through to socket fallback
            scapy = None

    # Socket fallback: send UDP and wait for any UDP response
    for p in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        try:
            sock.sendto(b"\x00", (host, p))
            data, _ = sock.recvfrom(1024)
            if data:
                results[p] = "open"
            else:
                results[p] = "open|filtered"
        except socket.timeout:
            results[p] = "open|filtered"
        except Exception:
            results[p] = "error"
        finally:
            sock.close()

    return results


