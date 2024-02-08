import socket
from threading import Lock
from time import sleep

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from arbol import aprint

from microplugins.network.discover_worker import DiscoverWorker


class CodeDropClient(QObject):
    def __init__(self, multicast_group):
        super().__init__()
        self.multicast_group = multicast_group
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

        # Create a worker and move it to a thread:
        self.discover_thread = QThread()
        self.discover_worker = DiscoverWorker(self.multicast_group)
        self.discover_worker.moveToThread(self.discover_thread)

        # Ensure the thread is properly stopped and cleaned up before exiting
        self.discover_thread.started.connect(
            self.discover_worker.discover_servers)
        self.discover_worker.server_discovered.connect(self.update_servers)
        self.discover_worker.error.connect(self.handle_error)

        # Cleanup on completion
        self.discover_worker.finished.connect(self.discover_thread.quit)
        self.discover_worker.finished.connect(self.discover_worker.deleteLater)
        self.discover_thread.finished.connect(self.discover_thread.deleteLater)

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

    def update_servers(self, server_name, server_address, server_port):
        self.servers[server_name] = (server_address, server_port)
        # Update your GUI or data structure with new server information here

    def send_message(self, server_name, message):
        if server_name in self.servers:
            server_address, server_port = self.servers[server_name]

            with self.sending_lock:
                # Check if there's already a thread running for sending messages:
                max_number_of_attempts: int = 10
                while self.send_thread is not None and self.send_worker is not None:
                    aprint("A send thread is already running. Wait for it to finish.")
                    sleep(1)
                    max_number_of_attempts -= 1

                    # If the thread is taking too long, stop waiting and don't send the message:
                    if max_number_of_attempts == 0:
                        aprint("Max number of attempts reached. Can't send message.")
                        return


                # Create a QThread each time for sending messages
                self.send_thread = QThread()

                # Create a worker to send the message and move it to the thread:
                self.send_worker = self.create_send_worker(server_address, server_port, message)
                self.send_worker.moveToThread(self.send_thread)

                # Connect the thread started signal to the worker's send method:
                self.send_thread.started.connect(self.send_worker.send)

                # Cleanup on completion
                self.send_worker.finished.connect(self.send_thread.quit)
                self.send_worker.finished.connect(self.send_worker.deleteLater)

                # When the thread is done, clean it up:
                self.send_thread.finished.connect(self.send_thread.deleteLater)

                # Start the thread:
                self.send_thread.start()
                aprint(f"Sending message of length: {len(message)} to {server_name} at {server_address}:{server_port}")
        else:
            print(f"Server {server_name} not found.")

    def create_send_worker(self, server_address, server_port, message):

        parent_self = self
        class SendWorker(QObject):
            finished = pyqtSignal()
            @pyqtSlot()
            def send(self):
                with parent_self.sending_lock:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((server_address, server_port))
                        sock.sendall(message.encode())
                        aprint(f"Message of length: {len(message)} sent to {server_address}:{server_port}")

                    except Exception as e:
                        aprint(f"Error sending message: {e}")
                    finally:
                        sock.close()
                        self.finished.emit()
                        parent_self.send_thread = None
                        parent_self.send_worker = None

        return SendWorker()

    def handle_error(self, e):
        aprint(f"Error: {e}")

    def stop_discovering(self):
        self.discover_worker.stop()
        self.discover_thread.quit()
        self.discover_thread.wait()