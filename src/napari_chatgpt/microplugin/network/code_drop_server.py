"""Server for receiving code snippets over the local network via CodeDrop.

Broadcasts its presence via UDP multicast so that ``CodeDropClient`` instances
can discover it, and listens for incoming TCP connections carrying code
snippet messages.
"""

import random
import socket
import struct
from collections.abc import Callable

from arbol import aprint
from qtpy.QtCore import QObject, QThread

from napari_chatgpt.microplugin.network.broadcast_worker import BroadcastWorker
from napari_chatgpt.microplugin.network.receive_worker import ReceiveWorker


class CodeDropServer(QObject):
    """Server that broadcasts its presence and receives code snippets over TCP.

    Uses a ``BroadcastWorker`` to periodically announce itself on UDP
    multicast groups and a ``ReceiveWorker`` to accept incoming TCP
    connections carrying code snippet messages.

    Attributes:
        multicast_groups: List of ``(address, port)`` multicast destinations.
        server_hostname: Hostname of this machine.
        server_port: TCP port the server listens on for incoming messages.
        callback: Function called with ``(address, message)`` when a
            message is received.
    """

    _code_drop_multicast_groups = [("224.1.1.1", 5007), ("224.1.1.1", 5008)]

    def __init__(
        self,
        callback: Callable,
        multicast_groups=None,
        server_port: int | None = None,
    ):
        """Initialize the CodeDrop server.

        Args:
            callback: Function called as ``callback(addr, message)`` when
                a message is received from a client.
            multicast_groups: Optional list of ``(address, port)`` tuples
                for multicast broadcasting. Defaults to
                ``_code_drop_multicast_groups``.
            server_port: TCP port to listen on. If ``None``, a random
                available port in the range 5000--5100 is chosen.
        """
        super().__init__()

        if multicast_groups is None:
            # choose a random multicast group:
            multicast_groups = CodeDropServer._code_drop_multicast_groups
            aprint(f"Multicast group: {multicast_groups}")

        if server_port is None:
            # choose a random valid port number:
            server_port = self._find_port()
            aprint(f"Server port chosen: {server_port}")

        # Store the multicast group:
        self.multicast_groups = multicast_groups

        # This machine's hostname:
        self.server_hostname = socket.gethostname()

        # Store the server port number:
        self.server_port = server_port

        # Store the callback function:
        self.callback = callback

        # Create a socket for broadcasting:
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", 32)
        )

        # Setup the broadcast worker and thread:
        self.broadcast_thread = QThread()
        self.broadcast_thread.setTerminationEnabled(True)
        self.broadcast_thread.setObjectName("BroadcastThread")
        self.broadcast_worker = BroadcastWorker(
            self.broadcast_socket, self.multicast_groups, self.server_port
        )
        self.broadcast_worker.moveToThread(self.broadcast_thread)
        self.broadcast_thread.started.connect(self.broadcast_worker.broadcast)
        self.broadcast_worker.error.connect(self.handle_error)

        # Setup the receive worker and thread:
        self.receive_thread = QThread()
        self.receive_thread.setTerminationEnabled(True)
        self.receive_thread.setObjectName("ReceiveThread")
        self.receive_worker = ReceiveWorker(self.server_port)
        self.receive_worker.moveToThread(self.receive_thread)
        self.receive_thread.started.connect(self.receive_worker.receive_messages)
        self.receive_worker.message_received.connect(
            lambda addr, msg: self.callback(addr, msg)
        )
        self.receive_worker.error.connect(self.handle_error)

    def _find_port(self):
        """Find an available TCP port in the range 5000--5100.

        Returns:
            An available port number.
        """
        port = 5000 + random.randint(0, 100)
        while True:
            try:
                # check if the port is already in use:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(("", port))
                s.close()
                break
            except OSError:
                port = 5000 + random.randint(0, 100)
        return port

    def start_broadcasting(self):
        """Start the multicast broadcast background thread."""
        self.broadcast_thread.start()

    def start_receiving(self):
        """Start the TCP message receiving background thread."""
        self.receive_thread.start()

    def stop_broadcasting(self):
        """Stop the broadcast worker and wait for its thread to finish."""
        if self.broadcast_worker and self.broadcast_thread:
            # Stop the broadcast worker and thread:
            self.broadcast_worker.stop()
            self.broadcast_thread.quit()
            self.broadcast_thread.wait()

    def stop_receiving(self):
        """Stop the receive worker and wait for its thread to finish."""
        if self.receive_worker and self.receive_thread:
            # Stop the receive worker and thread:
            self.receive_worker.stop()
            self.receive_thread.quit()
            self.receive_thread.wait()

    def stop(self):
        """Stop both broadcasting and receiving threads."""
        self.stop_broadcasting()
        self.stop_receiving()

    def handle_error(self, e):
        """Log an error from a worker thread."""
        aprint(f"Error: {e}")
