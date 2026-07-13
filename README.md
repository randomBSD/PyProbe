# PyProbe

PyProbe is a Python network discovery and diagnostics toolkit. This
repository contains a working prototype with a clean CLI, banner,
logging, and an extensible package layout aimed at network discovery,
scanning, and basic service probing.

Key features in this prototype
- ICMP ping sweeps (uses `scapy` when available, otherwise system `ping`)
- ARP sweeps (requires `scapy` + elevated privileges)
- TCP connect scanner (sync and async implementations)
- UDP probing with optional ICMP-unreachable detection (requires `scapy` + privileges)
- Basic probes: HTTP, SSH banner grab, FTP banner (with stdlib fallbacks)

Installation

Create a virtual environment and install recommended packages:

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Notes:
- `scapy` enables privileged packet operations (ARP, raw ICMP). Run the CLI
	as root/Administrator for full functionality.
- `rich` is optional for nicer terminal output; the CLI will fall back to plain text.

Quick usage

Show help:

```bash
python -m pyprobe --help
```

Examples:

```bash
# Ping sweep (prefers scapy if installed)
python -m pyprobe discover 192.168.1.0/24

# TCP scan (sync)
python -m pyprobe scan 10.0.0.5

# TCP scan (async) with high concurrency
python -m pyprobe scan 10.0.0.5 --async

# TCP + UDP combined
python -m pyprobe scan 10.0.0.5 --udp

# UDP-only scan
python -m pyprobe udp 10.0.0.5 --ports 53 161

# Probe an HTTP endpoint
python -m pyprobe probe http://example.com
```

Safety & legal

Only scan systems and networks you own or have explicit permission to test.
Unauthorized scanning can be illegal and disruptive. Include a clear authorization
statement in any published repository.

Next steps

- Add reporting exporters (JSON/HTML/Markdown) and a richer TUI using `rich`.
- Add unit tests and CI (GitHub Actions) before publishing publicly.

