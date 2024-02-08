import socket
import time

from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal



class ReceiveWorker(QObject):

    # Signal for received messages:
    message_received = pyqtSignal(tuple, str)  # Signal for received messages

    # Signal for errors:
    error = pyqtSignal(Exception)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.is_running = True

    def stop(self):
        self.is_running = False

    @pyqtSlot()
    def receive_messages(self):
        try:

            # Create a socket to listen for incoming connections:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to the port:
            server_socket.bind(('', self.port))

            # Listen for incoming connections:
            server_socket.listen(5)

            while self.is_running:
                try:
                    # Accept the connection:
                    client_socket, addr = server_socket.accept()
                    chunks = []
                    while True:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            break  # Connection is closed, and we've received the complete message.
                        chunks.append(chunk)

                    # Combine the chunks to form the complete message:
                    message = b''.join(chunks).decode()

                    # Emit the message received signal:
                    self.message_received.emit(addr, message)

                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.error.emit(e)

                finally:
                    # Close the client socket:
                    client_socket.close()


        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(e)
        finally:
            server_socket.close()