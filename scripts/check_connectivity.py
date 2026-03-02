"""Verbose connectivity checks for local backend and external network.

This script attempts HTTP(S) requests and raw TCP connects to help
diagnose failures caused by VPNs, firewalls, or host resolution.

Usage: python scripts/check_connectivity.py
"""
import urllib.request
import urllib.error
import socket
import traceback
import sys


def check_url(url: str, timeout: int = 5):
    """Attempt an HTTP request and print a verbose success/failure result."""
    print(f"-> Checking URL: {url}")
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            print(f"   OK: {url} -> {resp.status}")
    except Exception as e:
        print(f"   ERROR: {url} -> {e}")
        traceback.print_exc()


def check_socket(host: str, port: int, timeout: int = 3):
    """Attempt a low-level TCP connection to verify network reachability."""
    print(f"-> Testing TCP connect to {host}:{port}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        print(f"   OK: TCP connect to {host}:{port} succeeded")
    except Exception as e:
        print(f"   ERROR: TCP connect to {host}:{port} -> {e}")
        traceback.print_exc()
    finally:
        try:
            s.close()
        except Exception:
            pass


def main():
    """Run a sequence of local and external network diagnostics."""
    print(f"Python: {sys.version.splitlines()[0]}")

    print('\nLocal backend (127.0.0.1)')
    check_url('http://127.0.0.1:8000/api/kpis')
    check_socket('127.0.0.1', 8000)

    print('\nLocal backend (localhost)')
    check_url('http://localhost:8000/api/kpis')
    check_socket('localhost', 8000)

    print('\nExternal HTTPS test')
    check_url('https://www.microsoft.com')

    print('\nIf local TCP connections fail while the server process reports "Application startup complete", check for VPN kill-switch, firewall, or a hosts file overriding localhost.')


if __name__ == '__main__':
    main()
