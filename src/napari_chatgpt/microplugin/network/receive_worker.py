import socket

from arbol import aprint
from qtpy.QtCore import Slot, QObject, Signal


class ReceiveWorker(QObject):
    # Signal for received messages:
    message_received = Signal(tuple, str)  # Signal for received messages

    # Signal for errors:
    error = Signal(Exception)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.is_running = True

    def stop(self):
        self.is_running = False

    @Slot()
    def receive_messages(self):
        try:
            aprint(f"Listening for messages on port: {self.port}")

            # Create a socket to listen for incoming connections:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to the port:
            server_socket.bind(('', self.port))

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
                    message = b''.join(chunks).decode()

                    # Emit the message received signal:
                    self.message_received.emit(addr, message)

                except socket.timeout:
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
