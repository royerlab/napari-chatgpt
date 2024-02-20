import json
import os
import socket
from threading import Lock
from time import sleep

from arbol import aprint
from qtpy.QtCore import QObject, Signal, Slot, QThread

from microplugin.network.code_drop_server import CodeDropServer
from microplugin.network.discover_worker import DiscoverWorker


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

        self.discover_thread = QThread()
        self.discover_thread.setTerminationEnabled(True)
        self.discover_thread.setObjectName("DiscoverThread")
        self.discover_worker = DiscoverWorker(self.multicast_groups)
        self.discover_worker.moveToThread(self.discover_thread)

        # Ensure the thread is properly stopped and cleaned up before exiting
        self.discover_thread.started.connect(
            self.discover_worker.discover_servers)
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
        if self.discover_worker and self.discover_thread:
            # Ensure there's a stop method to signal the worker to terminate:
            self.discover_worker.stop()
            self.discover_thread.quit()
            self.discover_thread.wait()
            self.discover_thread = None

    def update_servers(self, user_name, server_name, server_address,
                       server_port):

        # Server name and port are the key:
        key = f"{server_name}:{server_port}"

        self.servers[key] = (user_name, server_address, server_port)
        # Update your GUI or data structure with new server information here

    def send_code_message(self,
                          server_address: str,
                          server_port: int,
                          filename: str,
                          code: str):

        # get hostname:
        hostname = socket.gethostname()

        # Get username (login) from the system:
        username = os.getlogin()

        # Message dict:
        message_dict = {
            'hostname': hostname,
            'username': username,
            'filename': filename,
            'code': code}

        # Convert dict to JSON string:
        message_str = json.dumps(message_dict)

        # Send message:
        self.send_message_by_address(server_address,
                                     server_port,
                                     message_str)

    def send_message_by_address(self,
                                server_address: str,
                                server_port: int,
                                message: str):

        with self.sending_lock:
            # Check if there's already a thread running for sending messages:
            max_number_of_attempts: int = 10
            while self.send_thread is not None and self.send_thread.isRunning():
                self.send_thread.quit()
                self.send_thread.wait()

                aprint(
                    "A send thread is already running. Wait for it to finish.")
                sleep(0.1)
                max_number_of_attempts -= 1

                # If the thread is taking too long, stop waiting and don't send the message:
                if max_number_of_attempts == 0:
                    aprint(
                        "Max number of attempts reached. Can't send message.")
                    return

            # Create a QThread each time for sending messages
            self.send_thread = QThread()
            self.send_thread.setTerminationEnabled(True)
            self.send_thread.setObjectName("SendThread")

            # Create a worker to send the message and move it to the thread:
            self.send_worker = self.create_send_worker(server_address,
                                                       server_port, message)
            self.send_worker.moveToThread(self.send_thread)

            # Connect the thread started signal to the worker's send method:
            self.send_thread.started.connect(self.send_worker.send)

            # Start the thread:
            self.send_thread.start()
            aprint(
                f"Sending message of length: {len(message)} to {server_address}:{server_port}")

    def create_send_worker(self, server_address, server_port, message):

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
                            f"Message of length: {len(message)} sent to {server_address}:{server_port}")

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
        self.stop_discovering()



