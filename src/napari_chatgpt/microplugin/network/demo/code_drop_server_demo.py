"""Demo script for the CodeDrop server.

Starts a ``CodeDropServer`` that broadcasts its presence on the local
network and prints any received messages to stdout.
"""

import sys

from qtpy.QtWidgets import QApplication

from napari_chatgpt.microplugin.network.code_drop_server import CodeDropServer


def server_message_received(addr, message):
    print(f"Message from {addr}: {message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = CodeDropServer(server_message_received)
    server.start_broadcasting()
    server.start_receiving()
    sys.exit(app.exec_())
