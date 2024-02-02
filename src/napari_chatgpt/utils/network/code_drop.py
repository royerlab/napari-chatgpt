import socket
import struct
import threading
import time


class CodeDropServer:
    def __init__(self, multicast_group, port, callback):
        self.hostname = socket.gethostname()
        self.multicast_group = multicast_group
        self.port = port
        self.callback = callback
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

    def start_broadcasting(self):
        threading.Thread(target=self.broadcast).start()

    def start_receiving(self):
        threading.Thread(target=self.receive_messages).start()

    def broadcast(self):
        while True:
            message = self.hostname.encode()
            self.sock.sendto(message, self.multicast_group)
            time.sleep(5)

    def receive_messages(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', self.port))
        server_socket.listen(5)
        while True:
            client_socket, addr = server_socket.accept()
            message = client_socket.recv(1024).decode()
            self.callback(addr, message)
            client_socket.close()



class CodeDropClient:
    def __init__(self, multicast_group, server_port):
        self.multicast_group = multicast_group
        self.server_port = server_port
        self.servers = {}  # Mapping server names to addresses

    def start_discovering(self):
        threading.Thread(target=self.discover_servers).start()

    def discover_servers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.multicast_group[1]))
        mreq = socket.inet_aton(self.multicast_group[0]) + struct.pack('=I', socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            data, addr = sock.recvfrom(1024)
            server_name = data.decode()
            self.servers[server_name] = addr[0]

    def send_message(self, server_name, message):
        if server_name in self.servers:
            server_address = self.servers[server_name]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server_address, self.server_port))
            sock.send(message.encode())
            sock.close()
        else:
            print(f"Server {server_name} not found.")




