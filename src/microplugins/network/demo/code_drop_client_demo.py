import sys

from PyQt5.QtWidgets import QApplication

from microplugins.network.code_drop_client import CodeDropClient
from microplugins.network.demo.code_drop_client_widget import \
    CodeDropClientWidget


def on_server_discovered(server_name, server_address):
    print(f"Discovered server: {server_name} at {server_address}")
    client.send_message(server_name, "Hello, Server!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    multicast_group = ('224.1.1.1', 5007)
    client = CodeDropClient(multicast_group)
    client.discover_worker.server_discovered.connect(on_server_discovered)
    client.start_discovering()

    # open a widget to send messages:
    #client_ui = CodeDropClientWidget(client)

    #client_ui.show()

    sys.exit(app.exec_())

    print(client)