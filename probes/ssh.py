"""SSH probing helpers (banner grab)."""
from __future__ import annotations

import socket
from typing import Dict


def probe_ssh(target: str, timeout: float = 3.0) -> Dict[str, str]:
    """Grab an SSH banner from target (host[:port] or host)."""
    host = target
    port = 22
    if ":" in target:
        try:
            host, port_str = target.split(":", 1)
            port = int(port_str)
        except Exception:
            pass

    try:
        s = socket.create_connection((host, port), timeout=timeout)
        # SSH servers send banner upon connect
        banner = s.recv(256).decode(errors="ignore").strip()
        s.close()
        return {"target": target, "banner": banner}
    except Exception as e:
        return {"target": target, "error": str(e)}

