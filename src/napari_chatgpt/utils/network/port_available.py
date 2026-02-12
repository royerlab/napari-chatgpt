"""Utilities for checking TCP port availability on localhost."""


def is_port_available(port: int):
    """Check if a TCP port is available on localhost.

    Args:
        port: The TCP port number to check.

    Returns:
        True if the port is available, False otherwise.
    """
    # Checks if TCP port is available on localhost:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0


def find_first_port_available(start: int, end: int):
    """Find the first available TCP port in a range.

    Args:
        start: The beginning of the port range (inclusive).
        end: The end of the port range (exclusive).

    Returns:
        The first available port number, or None if no port is available.
    """
    for port in range(start, end):
        if is_port_available(port):
            return port
    return None
