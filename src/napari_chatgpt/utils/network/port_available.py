def is_port_available(port: int):
    """
    Determine whether a TCP port on localhost is currently available.
    
    Parameters:
        port (int): The port number to check.
    
    Returns:
        bool: True if the port is available, False if it is in use.
    """
    # Checks if TCP port is available on localhost:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0


def find_first_port_available(start: int, end: int):
    """
    Return the first available TCP port on localhost within a specified range.
    
    Parameters:
        start (int): The starting port number (inclusive).
        end (int): The ending port number (exclusive).
    
    Returns:
        int or None: The first available port number, or None if no ports are available in the range.
    """
    for port in range(start, end):
        if is_port_available(port):
            return port
    return None
