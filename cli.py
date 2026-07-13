"""Command-line interface for PyProbe.

The CLI implemented here is intentionally small and easy to extend. It
prints a banner, performs a dependency check, and exposes placeholder
subcommands for discovery, scanning, probing, and reporting.
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from . import __version__
from .banner import show_banner
from .logger import get_logger
from .config import default_config
from .discovery import ping_discover, arp_discover, dns_lookup
from .scanner import scan_ports, tcp_scan, udp_scan
from .probes import probe_http, probe_ssh, probe_ftp


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pyprobe", description="PyProbe - Network discovery & diagnostics")
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    sub = parser.add_subparsers(dest="command", title="subcommands")

    p_discover = sub.add_parser("discover", help="Discover hosts on a network")
    p_discover.add_argument("network", nargs="?", help="Network in CIDR (e.g. 192.168.1.0/24)")

    p_scan = sub.add_parser("scan", help="Scan a host for open ports")
    p_scan.add_argument("host", nargs="?", help="Host or IP to scan")
    p_scan.add_argument("--async", dest="use_async", action="store_true", help="Use async TCP scanner for higher concurrency")
    p_scan.add_argument("--udp", dest="scan_udp", action="store_true", help="Also run UDP scan and show UDP statuses")

    p_probe = sub.add_parser("probe", help="Probe a service on a host")
    p_probe.add_argument("target", nargs="?", help="Host:port or URL to probe")

    p_report = sub.add_parser("report", help="Export a scan report")
    p_report.add_argument("file", nargs="?", help="Scan file to export")

    p_udp = sub.add_parser("udp", help="Perform a UDP scan")
    p_udp.add_argument("host", nargs="?", help="Host or IP to scan")
    p_udp.add_argument("--ports", nargs="*", type=int, help="Ports to scan (space separated) e.g. --ports 53 161 500")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point for the CLI.

    Args:
        argv: Optional argument vector (defaults to sys.argv[1:])

    Returns:
        Exit code integer.
    """
    logger = get_logger()
    if argv is None:
        argv = sys.argv[1:]

    parser = _build_parser()
    args = parser.parse_args(argv)

    # Show banner and dependency info on every run (can be silenced later)
    show_banner(__version__)

    if args.version:
        print(__version__)
        return 0

    cfg = default_config()
    logger.info("Using config: timeout=%s threads=%s", cfg.timeout, cfg.threads)

    if args.command == "discover":
        network = getattr(args, "network", None) or "127.0.0.1/32"
        logger.info("Discovering network: %s", network)
        results = ping_discover(network)
        print("Discovery results:")
        for r in results:
            print(" -", r)
        return 0

    if args.command == "scan":
        host = getattr(args, "host", None) or "127.0.0.1"
        logger.info("Scanning host: %s", host)
        ports = cfg.ports
        use_async = getattr(args, "use_async", False)
        scan_udp = getattr(args, "scan_udp", False)
        if use_async:
            try:
                import asyncio
                from .scanner import async_tcp_scan

                results = asyncio.run(async_tcp_scan(host, ports, timeout=cfg.timeout))
            except Exception as e:
                logger.error("Async scan failed: %s", e)
                results = scan_ports(host, ports)
        else:
            results = scan_ports(host, ports)

        # If UDP requested, run UDP scan and print combined table
        if scan_udp:
            from .scanner import udp_scan

            udp_results = udp_scan(host, ports, timeout=cfg.timeout)
        else:
            udp_results = {}

        # print combined table
        def _print_table(tcp_res, udp_res):
            ports_all = sorted(set(list(tcp_res.keys()) + list(udp_res.keys())))
            col_port = "Port"
            col_tcp = "TCP"
            col_udp = "UDP"
            w1 = max(6, max((len(str(p)) for p in ports_all), default=4))
            w2 = 8
            print(f"{col_port:<{w1}} {col_tcp:<{w2}} {col_udp}")
            print("-" * (w1 + w2 + 6))
            for p in ports_all:
                tcp_status = "open" if tcp_res.get(p) else "closed"
                udp_status = udp_res.get(p, "-")
                print(f"{p:<{w1}} {tcp_status:<{w2}} {udp_status}")

        _print_table(results, udp_results)
        return 0

    if args.command == "probe":
        target = getattr(args, "target", None) or "http://127.0.0.1"
        logger.info("Probing target: %s", target)
        # naive dispatch based on scheme or presence of ':'
        if target.startswith("http"):
            info = probe_http(target)
        elif ":" in target:
            # naive port-based guess: 22 -> ssh, 21 -> ftp
            if target.endswith(":22"):
                info = probe_ssh(target)
            elif target.endswith(":21"):
                info = probe_ftp(target)
            else:
                info = {"target": target, "info": "unknown-protocol"}
        else:
            info = {"target": target, "info": "no-probe-performed"}
        print("Probe result:", info)
        return 0

    if args.command == "report":
        file = getattr(args, "file", None) or "scan.json"
        logger.info("Exporting report: %s", file)
        print("(placeholder) export to", file)
        return 0

    if args.command == "udp":
        host = getattr(args, "host", None) or "127.0.0.1"
        ports = getattr(args, "ports", None) or cfg.ports
        from .scanner import udp_scan

        logger.info("UDP scanning host: %s", host)
        udp_results = udp_scan(host, ports, timeout=cfg.timeout)
        # print simple table
        print("UDP scan results for", host)
        for p in sorted(udp_results.keys()):
            print(f" - {p}: {udp_results[p]}")
        return 0

    # No subcommand provided; show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
