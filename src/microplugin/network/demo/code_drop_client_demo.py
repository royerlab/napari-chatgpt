import sys

from qtpy.QtWidgets import QApplication

from microplugin.network.code_drop_client import CodeDropClient


def on_server_discovered(server_name, server_address, server_port):
    print(f"Discovered server: {server_name} at {server_address}")
    client.send_message_by_address(server_address, server_port,
                                   "Hello, Server!")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    client = CodeDropClient()
    client.discover_worker.server_discovered.connect(on_server_discovered)
    client.start_discovering()

    # open a widget to send messages:
    # client_ui = CodeDropClientWidget(client)

    # client_ui.show()

    sys.exit(app.exec_())

    print(client)
