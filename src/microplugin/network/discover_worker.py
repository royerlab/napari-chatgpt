import socket
import struct
from time import sleep

from arbol import aprint
from qtpy.QtCore import Slot, QObject, Signal


class DiscoverWorker(QObject):
    # Signal for discovered servers:
    server_discovered = Signal(str, str, str,
                                   int)  # user_name, server_name, server_addr, server_port

    # Signal for errors:
    error = Signal(Exception)

    # Signal to indicate the worker has finished its work
    finished = Signal()

    def __init__(self, multicast_groups):
        super().__init__()
        self.multicast_groups = multicast_groups
        self.is_running = True
        self.is_enabled = True

    def stop(self):
        self.is_running = False

    def close(self):
        self.stop()

    @Slot()
    def discover_servers(self):
        try:
            available_multicast_group = None
            # Trying to bind to any of multicast groups (usefull for testing purposes):
            for multicast_group in self.multicast_groups:

                try:
                    # Create a socket to listen for multicast messages:
                    broadcast_listening_socket = socket.socket(socket.AF_INET,
                                                               socket.SOCK_DGRAM,
                                                               socket.IPPROTO_UDP)
                    broadcast_listening_socket.setsockopt(socket.SOL_SOCKET,
                                                          socket.SO_REUSEADDR,
                                                          1)

                    # Bind the socket to the multicast group:
                    broadcast_listening_socket.bind(('', multicast_group[1]))

                    # Store the multicast group that worked:
                    available_multicast_group = multicast_group

                    aprint(f"Bound to multicast group: {multicast_group}")

                    # If we reach this point without any exceptions, we can assume the socket is ready to receive messages:
                    break
                except OSError as e:
                    aprint(
                        f"Error binding to multicast group {multicast_group}: {e}")
                    import traceback
                    traceback.print_exc()
                    aprint(f"Most likely the multicast group is already in use by another instance of Omega! Only affects sending of code snippets.")

            # Tell the kernel to add the multicast group to the multicast group:
            mreq = struct.pack("4sl",
                               socket.inet_aton(available_multicast_group[0]),
                               socket.INADDR_ANY)

            # Join the multicast group:
            broadcast_listening_socket.setsockopt(socket.IPPROTO_IP,
                                                  socket.IP_ADD_MEMBERSHIP,
                                                  mreq)

            # Set a timeout of 5 seconds
            broadcast_listening_socket.settimeout(1.0)

            # Counter use to keep track of how many times we timedout
            counter = 0

            while self.is_running:

                try:

                    if self.is_enabled:
                        try:
                            # Receive the data and sender's address:
                            data, addr = broadcast_listening_socket.recvfrom(1024)
                            if data:
                                # Directly use the received data, assuming it's in 'hostname:port' format
                                server_info = data.decode().strip()
                                user_name, server_name, server_port = server_info.split(
                                    ':')
                                server_addr = addr[0]
                                server_port = int(server_port)
                                self.server_discovered.emit(user_name, server_name,
                                                            server_addr, server_port)
                            else:
                                break  # No more data, stop the loop
                        except socket.timeout:
                            counter = counter + 1
                            if counter > 30:
                                aprint("No servers discovered received within the last 30 seconds.")
                                counter = 0

                    else:
                        # If discovery is disabled, just sleep for a while:
                        sleep(0.5)

                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    self.error.emit(e)

                    # Note: exception handling is within the loop so that the thread doesn't die


        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(e)
        finally:
            broadcast_listening_socket.close()
            self.finished.emit()  # Emit finished signal when done
            return
