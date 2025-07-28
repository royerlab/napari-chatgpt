import json
import os
import socket
from threading import Lock
from time import sleep

from arbol import aprint
from qtpy.QtCore import QObject, Signal, Slot, QThread

from napari_chatgpt.microplugin.network.code_drop_server import CodeDropServer
from napari_chatgpt.microplugin.network.discover_worker import DiscoverWorker


class CodeDropClient(QObject):
    def __init__(self, multicast_groups=None):
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

        # Create a worker and move it to a thread

        """
        Initializes the server discovery mechanism by creating a worker in a dedicated thread and connecting relevant signals for server discovery and error handling.
        """
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
        if self.discover_thread is not None:
            # Start the thread and begin discovering servers:
            self.discover_thread.start()

    def stop_discovering(self):
        """
        Stops the server discovery process and cleans up the associated thread and worker.
        """
        if self.discover_worker and self.discover_thread:
            # Ensure there's a stop method to signal the worker to terminate:
            self.discover_worker.stop()
            self.discover_thread.quit()
            self.discover_thread.wait()
            self.discover_thread = None

    def update_servers(self, user_name, server_name, server_address, server_port):

        # Server name and port are the key:
        """
        Update the internal record of discovered servers with the provided server information.
        
        Parameters:
            user_name (str): The username associated with the discovered server.
            server_name (str): The name of the discovered server.
            server_address (str): The network address of the server.
            server_port (int): The port number on which the server is listening.
        """
        key = f"{server_name}:{server_port}"

        self.servers[key] = (user_name, server_address, server_port)
        # Update your GUI or data structure with new server information here

    def send_code_message(
        self, server_address: str, server_port: int, filename: str, code: str
    ):

        # get hostname:
        """
        Sends a code message containing the local hostname, system username, filename, and code content to a specified server.
        
        Parameters:
            server_address (str): The IP address of the target server.
            server_port (int): The port number of the target server.
            filename (str): The name of the file associated with the code.
            code (str): The code content to be sent.
        """
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

        """
        Send a message to a specified server address and port using a dedicated thread.
        
        Ensures only one send operation occurs at a time by acquiring a lock and waiting for any existing send thread to finish, up to a maximum number of attempts. If unable to proceed, aborts the send. Otherwise, creates and starts a new thread to send the message asynchronously.
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

        """
        Create a worker object for asynchronously sending a message to a specified server address and port.
        
        The returned worker emits a `finished` signal upon completion and handles errors by invoking the parent's error handler.
        """
        parent_self = self

        class SendWorker(QObject):
            finished = Signal()

            @Slot()
            def send(self):
                """
                Sends a message to the specified server address and port over a TCP connection.
                
                Attempts to connect and transmit the encoded message. On completion or error, emits a finished signal and cleans up resources.
                """
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
        aprint(f"Error: {e}")

    def stop(self):
        """
        Stops the client by halting the server discovery process.
        """
        self.stop_discovering()
