"""Client for discovering and sending code snippets to CodeDrop servers.

Provides network discovery of ``CodeDropServer`` instances via UDP multicast
and the ability to send code snippets to discovered servers over TCP.
"""

import json
import os
import socket
from threading import Lock
from time import sleep

from arbol import aprint
from qtpy.QtCore import QObject, QThread, Signal, Slot

from napari_chatgpt.microplugin.network.code_drop_server import CodeDropServer
from napari_chatgpt.microplugin.network.discover_worker import DiscoverWorker


class CodeDropClient(QObject):
    """Client that discovers CodeDrop servers and sends code snippets to them.

    Uses a ``DiscoverWorker`` running in a background ``QThread`` to listen
    for multicast announcements from servers, and provides methods to send
    code messages over TCP connections.

    Attributes:
        multicast_groups: Multicast groups to listen on for server discovery.
        servers: Mapping of ``"hostname:port"`` keys to
            ``(username, address, port)`` tuples for discovered servers.
    """

    def __init__(self, multicast_groups=None):
        """Initialize the CodeDrop client.

        Args:
            multicast_groups: Optional list of ``(address, port)`` tuples
                for multicast discovery. Defaults to the groups defined in
                ``CodeDropServer._code_drop_multicast_groups``.
        """
        super().__init__()

        if multicast_groups is None:
            multicast_groups = CodeDropServer._code_drop_multicast_groups

        self.multicast_groups = multicast_groups
        self.servers = {}  # Mapping server names to addresses

        # Store thread and worker references to prevent premature garbage collection
        self.discover_thread = None
        self.discover_worker = None
        self.send_thread = None
        self.send_worker = None

        # initialise locks:
        self.sending_lock = Lock()

        self.init_discovery()

    def init_discovery(self):
        """Initialize the server discovery worker and its background thread."""

        # Create a worker and move it to a thread

        self.discover_thread = QThread()
        self.discover_thread.setTerminationEnabled(True)
        self.discover_thread.setObjectName("DiscoverThread")
        self.discover_worker = DiscoverWorker(self.multicast_groups)
        self.discover_worker.moveToThread(self.discover_thread)

        # Ensure the thread is properly stopped and cleaned up before exiting
        self.discover_thread.started.connect(self.discover_worker.discover_servers)
        self.discover_worker.server_discovered.connect(self.update_servers)
        self.discover_worker.error.connect(self.handle_error)

        # Cleanup on completion
        # self.discover_worker.finished.connect(self.discover_thread.quit)
        # self.discover_worker.finished.connect(self.discover_worker.deleteLater)
        # self.discover_thread.finished.connect(self.discover_thread.deleteLater)

    def start_discovering(self):
        """Start the server discovery background thread."""
        if self.discover_thread is not None:
            # Start the thread and begin discovering servers:
            self.discover_thread.start()

    def stop_discovering(self):
        """Stop the server discovery worker and wait for its thread to finish."""
        if self.discover_worker and self.discover_thread:
            # Ensure there's a stop method to signal the worker to terminate:
            self.discover_worker.stop()
            self.discover_thread.quit()
            self.discover_thread.wait()
            self.discover_thread = None

    def update_servers(self, user_name, server_name, server_address, server_port):
        """Update the discovered servers registry.

        Args:
            user_name: Username of the server operator.
            server_name: Hostname of the server machine.
            server_address: IP address of the server.
            server_port: TCP port the server listens on.
        """

        # Server name and port are the key:
        key = f"{server_name}:{server_port}"

        self.servers[key] = (user_name, server_address, server_port)
        # Update your GUI or data structure with new server information here

    def send_code_message(
        self, server_address: str, server_port: int, filename: str, code: str
    ):
        """Send a code snippet to a specific server.

        Packages the code along with sender metadata (hostname, username)
        into a JSON message and sends it via TCP.

        Args:
            server_address: IP address of the target server.
            server_port: TCP port of the target server.
            filename: Name of the code snippet file.
            code: Python source code to send.
        """

        # get hostname:
        hostname = socket.gethostname()

        # Get username (login) from the system:
        username = os.getlogin()

        # Message dict:
        message_dict = {
            "hostname": hostname,
            "username": username,
            "filename": filename,
            "code": code,
        }

        # Convert dict to JSON string:
        message_str = json.dumps(message_dict)

        # Send message:
        self.send_message_by_address(server_address, server_port, message_str)

    def send_message_by_address(
        self, server_address: str, server_port: int, message: str
    ):
        """Send a raw string message to a server in a background thread.

        Waits for any in-progress send to complete before starting a new
        one. Gives up after 10 failed attempts to acquire the send slot.

        Args:
            server_address: IP address of the target server.
            server_port: TCP port of the target server.
            message: The message string to send.
        """

        with self.sending_lock:
            # Check if there's already a thread running for sending messages:
            max_number_of_attempts: int = 10
            while self.send_thread is not None and self.send_thread.isRunning():
                self.send_thread.quit()
                self.send_thread.wait()

                aprint("A send thread is already running. Wait for it to finish.")
                sleep(0.1)
                max_number_of_attempts -= 1

                # If the thread is taking too long, stop waiting and don't send the message:
                if max_number_of_attempts == 0:
                    aprint("Max number of attempts reached. Can't send message.")
                    return

            # Create a QThread each time for sending messages
            self.send_thread = QThread()
            self.send_thread.setTerminationEnabled(True)
            self.send_thread.setObjectName("SendThread")

            # Create a worker to send the message and move it to the thread:
            self.send_worker = self.create_send_worker(
                server_address, server_port, message
            )
            self.send_worker.moveToThread(self.send_thread)

            # Connect the thread started signal to the worker's send method:
            self.send_thread.started.connect(self.send_worker.send)

            # Start the thread:
            self.send_thread.start()
            aprint(
                f"Sending message of length: {len(message)} to {server_address}:{server_port}"
            )

    def create_send_worker(self, server_address, server_port, message):
        """Create a QObject worker that sends a message over a TCP socket.

        Args:
            server_address: IP address of the target server.
            server_port: TCP port of the target server.
            message: The message string to send.

        Returns:
            A ``SendWorker`` instance ready to be moved to a ``QThread``.
        """

        parent_self = self

        class SendWorker(QObject):
            finished = Signal()

            @Slot()
            def send(self):
                with parent_self.sending_lock:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((server_address, server_port))
                        sock.sendall(message.encode())
                        aprint(
                            f"Message of length: {len(message)} sent to {server_address}:{server_port}"
                        )

                    except Exception as e:
                        aprint(f"Error sending message: {e}")
                        import traceback

                        traceback.print_exc()
                        parent_self.handle_error(e)
                    finally:
                        sock.close()
                        self.finished.emit()
                        parent_self.send_worker = None

        return SendWorker()

    def handle_error(self, e):
        """Log an error from a worker thread."""
        aprint(f"Error: {e}")

    def stop(self):
        """Stop all background threads (discovery and sending)."""
        self.stop_discovering()
