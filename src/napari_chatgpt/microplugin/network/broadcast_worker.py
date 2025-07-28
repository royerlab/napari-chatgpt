import os
import socket
import time

from qtpy.QtCore import Slot, QObject, Signal


class BroadcastWorker(QObject):
    error = Signal(Exception)

    def __init__(self, sock, multicast_groups, port, broadcast_interval: int = 1):
        """
        Initialize a BroadcastWorker to periodically send multicast messages.
        
        Parameters:
            sock: The socket used for sending broadcast messages.
            multicast_groups: List of multicast group addresses to which messages will be sent.
            port: Port number for broadcasting.
            broadcast_interval (int, optional): Interval in seconds between broadcasts. Defaults to 1.
        """
        super().__init__()

        # Store the socket object:
        self.sock = sock

        # Multicast group address:
        self.multicast_groups = multicast_groups

        # Port number that the server listens on:
        self.port = port

        # Broadcast interval:
        self.broadcast_interval = broadcast_interval

        # Flags to control the worker:
        self.is_enabled = True
        self.is_running = True

    def set_enabled(self, enabled):
        self.is_enabled = enabled

    def stop(self):
        self.is_running = False

    @Slot()
    def broadcast(self):

        # Run the broadcast loop:
        """
        Periodically sends multicast broadcast messages containing the current username, hostname, and port to all configured multicast groups.
        
        The method runs in a loop controlled by internal flags, and emits an error signal if an exception occurs, allowing the broadcast process to continue.
        """
        while self.is_running:
            try:
                if self.is_enabled:
                    for self.multicast_group in self.multicast_groups:
                        # get hostname:
                        hostname = socket.gethostname()

                        # get username:
                        username = os.getlogin()

                        # Format the message to include hostname and port
                        message = f"{username}:{hostname}:{self.port}".encode()

                        # Send the message to the multicast group:
                        self.sock.sendto(message, self.multicast_group)
                else:
                    # If the broadcast is disabled, just sleep for a while
                    pass

                time.sleep(self.broadcast_interval)

            # Handle exceptions and emit an error signal:
            except Exception as e:
                import traceback

                traceback.print_exc()
                self.error.emit(e)

                # Note: exception handling is within the loop so that the thread doesn't die
