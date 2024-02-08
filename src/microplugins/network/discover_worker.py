import socket
import struct

from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal

class DiscoverWorker(QObject):

    # Signal for discovered servers:
    server_discovered = pyqtSignal(str, str, int)  # server info in 'hostname:port' format

    # Signal for errors:
    error = pyqtSignal(Exception)

    # Signal to indicate the worker has finished its work
    finished = pyqtSignal()

    def __init__(self, multicast_group):
        super().__init__()
        self.multicast_group = multicast_group
        self.is_running = True

    def stop(self):
        self.is_running = False

    @pyqtSlot()
    def discover_servers(self):
        try:
            # Create a socket to listen for multicast messages:
            broadcast_listening_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            broadcast_listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind the socket to the multicast group:
            broadcast_listening_socket.bind(('', self.multicast_group[1]))

            # Tell the kernel to add the multicast group to the multicast group:
            mreq = struct.pack("4sl", socket.inet_aton(self.multicast_group[0]), socket.INADDR_ANY)

            # Join the multicast group:
            broadcast_listening_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            while self.is_running:
                data, addr = broadcast_listening_socket.recvfrom(1024)
                if data:
                    # Directly use the received data, assuming it's in 'hostname:port' format
                    server_info = data.decode().strip()
                    server_name, server_port = server_info.split(':')
                    server_addr = addr[0]
                    server_port = int(server_port)
                    self.server_discovered.emit(server_name, server_addr, server_port)
                else:
                    break  # No more data, stop the loop
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(e)
        finally:
            broadcast_listening_socket.close()
            self.finished.emit()  # Emit finished signal when done
