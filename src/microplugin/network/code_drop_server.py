import random
import socket
import struct
from typing import Optional, Callable

from arbol import aprint
from qtpy.QtCore import QObject, QThread

from microplugin.network.broadcast_worker import BroadcastWorker
from microplugin.network.receive_worker import ReceiveWorker


class CodeDropServer(QObject):
    _code_drop_multicast_groups = [('224.1.1.1', 5007), ('224.1.1.1', 5008)]

    def __init__(self,
                 callback: Callable,
                 multicast_groups=None,
                 server_port: Optional[int] = None):
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
        self.broadcast_socket.setsockopt(socket.IPPROTO_IP,
                                         socket.IP_MULTICAST_TTL, struct.pack('b', 32) )

        # Setup the broadcast worker and thread:
        self.broadcast_thread = QThread()
        self.broadcast_thread.setTerminationEnabled(True)
        self.broadcast_thread.setObjectName("BroadcastThread")
        self.broadcast_worker = BroadcastWorker(self.broadcast_socket,
                                                self.multicast_groups,
                                                self.server_port)
        self.broadcast_worker.moveToThread(self.broadcast_thread)
        self.broadcast_thread.started.connect(self.broadcast_worker.broadcast)
        self.broadcast_worker.error.connect(self.handle_error)

        # Setup the receive worker and thread:
        self.receive_thread = QThread()
        self.receive_thread.setTerminationEnabled(True)
        self.receive_thread.setObjectName("ReceiveThread")
        self.receive_worker = ReceiveWorker(self.server_port)
        self.receive_worker.moveToThread(self.receive_thread)
        self.receive_thread.started.connect(
            self.receive_worker.receive_messages)
        self.receive_worker.message_received.connect(
            lambda addr, msg: self.callback(addr, msg))
        self.receive_worker.error.connect(self.handle_error)

    def _find_port(self):
        port = 5000 + random.randint(0, 100)
        while True:
            try:
                # check if the port is already in use:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('', port))
                s.close()
                break
            except OSError:
                port = 5000 + random.randint(0, 100)
        return port

    def start_broadcasting(self):
        self.broadcast_thread.start()

    def start_receiving(self):
        self.receive_thread.start()

    def stop_broadcasting(self):
        if self.broadcast_worker and self.broadcast_thread:
            # Stop the broadcast worker and thread:
            self.broadcast_worker.stop()
            self.broadcast_thread.quit()
            self.broadcast_thread.wait()

    def stop_receiving(self):
        if self.receive_worker and self.receive_thread:
            # Stop the receive worker and thread:
            self.receive_worker.stop()
            self.receive_thread.quit()
            self.receive_thread.wait()

    def stop(self):
        self.stop_broadcasting()
        self.stop_receiving()


    def handle_error(self, e):
        aprint(f"Error: {e}")


