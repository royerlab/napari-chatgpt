"""Qt worker that periodically broadcasts server presence via UDP multicast.

Used by ``CodeDropServer`` to announce its availability on the local
network so that ``DiscoverWorker`` instances on other machines can find it.
"""

import os
import socket
import time

from qtpy.QtCore import QObject, Signal, Slot


class BroadcastWorker(QObject):
    """Worker that broadcasts server identity over UDP multicast at regular intervals.

    Sends messages containing ``username:hostname:port`` to configured
    multicast groups so that clients can discover this server.

    Attributes:
        error: Signal emitted when an exception occurs during broadcasting.
        sock: UDP socket used for sending multicast datagrams.
        multicast_groups: List of ``(address, port)`` tuples to broadcast to.
        port: TCP port number of the server being advertised.
        broadcast_interval: Seconds between broadcast messages.
        is_enabled: Whether broadcasting is currently active.
        is_running: Whether the worker loop should continue running.
    """

    error = Signal(Exception)

    def __init__(self, sock, multicast_groups, port, broadcast_interval: int = 1):
        """Initialize the broadcast worker.

        Args:
            sock: Pre-configured UDP socket for multicast transmission.
            multicast_groups: List of ``(address, port)`` tuples for
                multicast destinations.
            port: TCP port number of the server to advertise.
            broadcast_interval: Seconds between consecutive broadcasts.
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
        """Enable or disable broadcasting."""
        self.is_enabled = enabled

    def stop(self):
        """Signal the broadcast loop to stop."""
        self.is_running = False

    @Slot()
    def broadcast(self):
        """Run the broadcast loop, sending identity messages to multicast groups.

        This method is intended to be executed in a ``QThread``. It loops
        until ``stop()`` is called, sending a ``username:hostname:port``
        message to each multicast group at the configured interval.
        """

        # Run the broadcast loop:
        while self.is_running:
            try:
                if self.is_enabled:
                    for multicast_group in self.multicast_groups:
                        # get hostname:
                        hostname = socket.gethostname()

                        # get username:
                        username = os.getlogin()

                        # Format the message to include hostname and port
                        message = f"{username}:{hostname}:{self.port}".encode()

                        # Send the message to the multicast group:
                        self.sock.sendto(message, multicast_group)
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
