"""FTP probing helpers using ftplib."""
from __future__ import annotations

from typing import Dict


def probe_ftp(target: str, timeout: float = 5.0) -> Dict[str, str]:
    """Connect to FTP server and return welcome banner or error."""
    import socket

    host = target
    port = 21
    if ":" in target:
        try:
            host, port_str = target.split(":", 1)
            port = int(port_str)
        except Exception:
            pass

    try:
        import ftplib

        ftp = ftplib.FTP()
        ftp.connect(host, port, timeout=timeout)
        welcome = ftp.getwelcome()
        ftp.close()
        return {"target": target, "banner": welcome}
    except Exception as e:
        # fallback: try raw socket to read banner
        try:
            s = socket.create_connection((host, port), timeout=timeout)
            data = s.recv(512).decode(errors="ignore").strip()
            s.close()
            return {"target": target, "banner": data}
        except Exception:
            return {"target": target, "error": str(e)}

