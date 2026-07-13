"""HTTP probing helpers using `requests` or a socket fallback."""
from __future__ import annotations

from typing import Dict


def probe_http(url: str, timeout: float = 3.0) -> Dict[str, str]:
    """Probe an HTTP endpoint and return simple metadata.

    Tries `requests` if available, otherwise uses a basic socket
    connection to perform a HEAD request.
    """
    try:
        import requests  # type: ignore

        resp = requests.get(url, timeout=timeout)
        return {"url": url, "status_code": str(resp.status_code), "server": resp.headers.get("Server", "")}
    except Exception:
        # basic socket fallback
        from urllib.parse import urlparse
        import socket

        parsed = urlparse(url)
        host = parsed.hostname or url
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            s = socket.create_connection((host, port), timeout=timeout)
            request = f"HEAD {parsed.path or '/'} HTTP/1.0\r\nHost: {host}\r\n\r\n"
            s.send(request.encode())
            data = s.recv(1024).decode(errors="ignore")
            s.close()
            status_line = data.splitlines()[0] if data else ""
            server = ""
            for line in data.splitlines():
                if line.lower().startswith("server:"):
                    server = line.partition(":")[2].strip()
                    break
            return {"url": url, "status": status_line, "server": server}
        except Exception:
            return {"url": url, "error": "unreachable"}

