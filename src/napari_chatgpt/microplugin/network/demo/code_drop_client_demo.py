import sys

from qtpy.QtWidgets import QApplication

from napari_chatgpt.microplugin.network.code_drop_client import CodeDropClient


def on_server_discovered(server_name, server_address, server_port):
    """
    Handles the event when a server is discovered by printing its details and sending a greeting message to it.
    
    Parameters:
        server_name (str): The name of the discovered server.
        server_address (str): The network address of the discovered server.
        server_port (int): The port number of the discovered server.
    """
    print(f"Discovered server: {server_name} at {server_address}")
    client.send_message_by_address(server_address, server_port, "Hello, Server!")


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
