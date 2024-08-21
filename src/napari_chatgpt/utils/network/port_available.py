
def is_port_available(port: int):
    """
    Checks if a TCP port is available on localhost.
    Parameters
    ----------
    port : int

    Returns
    -------
    True if the port is available, False otherwise.

    """
    # Checks if TCP port is available on localhost:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_first_port_available(start: int, end: int):
    """
    Finds the first available port in a range.
    Parameters
    ----------
    start : int
    end : int

    Returns
    -------
    The first available port in the range, or None if no port is available.

    """
    for port in range(start, end):
        if is_port_available(port):
            return port
    return None