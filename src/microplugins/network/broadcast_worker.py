import socket
import time

from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal

class BroadcastWorker(QObject):
    error = pyqtSignal(Exception)

    def __init__(self, sock, multicast_group, port):
        super().__init__()

        # Store the socket object:
        self.sock = sock

        # Multicast group address:
        self.multicast_group = multicast_group

        # Port number that the server listens on:
        self.port = port

        # Flags to control the worker:
        self.is_enabled = True
        self.is_running = True

    def stop(self):
        self.is_running = False

    def set_enabled(self, enabled):
        self.is_enabled = enabled

    @pyqtSlot()
    def broadcast(self):
        try:
            while self.is_running:
                if self.is_enabled:
                    # Format the message to include hostname and port
                    message = f"{socket.gethostname()}:{self.port}".encode()

                    # Send the message to the multicast group:
                    self.sock.sendto(message, self.multicast_group)
                else:
                    # If the broadcast is disabled, just sleep for a while
                    pass

                time.sleep(5)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(e)
