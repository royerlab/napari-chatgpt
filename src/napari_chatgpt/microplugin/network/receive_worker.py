"""Qt worker that listens for incoming TCP messages from CodeDrop clients.

Runs a TCP server in a background thread, accepting connections and
reading complete messages which are then emitted via Qt signals.
"""

import socket

from arbol import aprint
from qtpy.QtCore import QObject, Signal, Slot


class ReceiveWorker(QObject):
    """Worker that accepts TCP connections and receives code snippet messages.

    Binds to a TCP port and listens for incoming connections. Each
    connection is read until closed, and the complete message is emitted
    via the ``message_received`` signal.

    Attributes:
        message_received: Signal emitted with ``(address_tuple, message_str)``
            for each received message.
        error: Signal emitted when an exception occurs.
        port: TCP port to listen on.
        is_running: Whether the worker loop should continue.
    """

    # Signal for received messages:
    message_received = Signal(tuple, str)  # Signal for received messages

    # Signal for errors:
    error = Signal(Exception)

    def __init__(self, port):
        """Initialize the receive worker.

        Args:
            port: TCP port number to bind and listen on.
        """
        super().__init__()
        self.port = port
        self.is_running = True

    def stop(self):
        """Signal the receive loop to stop."""
        self.is_running = False

    @Slot()
    def receive_messages(self):
        """Run the TCP server loop, accepting and reading incoming messages.

        Creates a TCP server socket, binds to the configured port, and
        loops accepting connections with a 1-second timeout. Each
        connection is read in 1024-byte chunks until closed, then the
        complete message is emitted via ``message_received``. Runs until
        ``stop()`` is called.
        """
        try:
            aprint(f"Listening for messages on port: {self.port}")

            # Create a socket to listen for incoming connections:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to the port:
            server_socket.bind(("", self.port))

            # Listen for incoming connections:
            server_socket.listen(5)

            # Set a timeout of 1 seconds
            server_socket.settimeout(1.0)

            while self.is_running:
                try:
                    client_socket = None

                    # Accept the connection:
                    client_socket, addr = server_socket.accept()
                    aprint(f"Connection from: {addr}")

                    chunks = []
                    while True:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            break  # Connection is closed, and we've received the complete message.
                        chunks.append(chunk)

                    # Combine the chunks to form the complete message:
                    message = b"".join(chunks).decode()

                    # Emit the message received signal:
                    self.message_received.emit(addr, message)

                except TimeoutError:
                    # No biggie! Just keep listening:
                    pass

                except Exception as e:
                    # That's a biggie! Emit the error signal:
                    import traceback

                    traceback.print_exc()
                    self.error.emit(e)

                finally:
                    # Close the client socket:
                    if client_socket:
                        client_socket.close()

        except Exception as e:
            import traceback

            traceback.print_exc()
            self.error.emit(e)
        finally:
            server_socket.close()
