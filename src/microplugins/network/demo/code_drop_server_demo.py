import sys

from PyQt5.QtWidgets import QApplication

from microplugins.network.code_drop_server import CodeDropServer

def server_message_received(addr, message):
    print(f"Message from {addr}: {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    multicast_group = ('224.1.1.1', 5007)
    server = CodeDropServer(multicast_group, server_message_received)
    server.start_broadcasting()
    server.start_receiving()
    sys.exit(app.exec_())