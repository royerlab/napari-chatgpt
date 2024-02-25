from typing import Callable, Tuple

from arbol import aprint
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QWidget, QPushButton, QComboBox, \
    QSizePolicy, QHBoxLayout

from microplugin.network.code_drop_client import CodeDropClient


class CodeDropSendWidget(QWidget):
    def __init__(self,
                 code_drop_client: CodeDropClient,
                 max_height: int = 50,
                 margin: int = 0,
                 refresh_interval: int = 1):

        super().__init__()

        # Code Drop Client:
        self.code_drop_client = code_drop_client

        # Initialize widgets:
        self.initUI(max_height=max_height,
                    margin=margin)

        # Refresh interval, converting from seconds to milliseconds:
        self.refresh_interval = refresh_interval * 1000

        # field for timer:
        self.timer = None


    def initUI(self, max_height: int,
               margin: int):

        # Layout:
        layout = QHBoxLayout(self)

        # Server selection dropdown
        self.username_address_port_combo_box = QComboBox()
        layout.addWidget(self.username_address_port_combo_box)

        # Send message button
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_code)
        self.send_button.setSizePolicy(QSizePolicy.Maximum,
                                       QSizePolicy.Maximum)  # Adjust size policy
        layout.addWidget(self.send_button)

        # Cancel message button
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.canceled)
        self.cancel_button.setSizePolicy(QSizePolicy.Maximum,
                                         QSizePolicy.Maximum)  # Adjust size policy
        layout.addWidget(self.cancel_button)

        # Set the layout margins:
        layout.setContentsMargins(margin,
                                  margin,
                                  margin,
                                  margin)
        # Set the layout:
        self.setLayout(layout)

        # Set the vertical size policy to Minimum so it takes the least vertical space
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Attempt to directly control the widget's size
        self.setMaximumHeight(max_height)  # Adjust 100 to your needs

        # Hide the widget initially:
        self.hide()

    def update_server_list(self):

        def _identifier(username_address_port):
            if not username_address_port:
                return None
            username, address, port = username_address_port
            return f'{username}:{address}:{str(port)}'

        # Assume that the combination of address and port is unique for each server and remains constant.
        # Save the current selection based on a unique identifier (e.g., address and port):
        current_selection = self.username_address_port_combo_box.currentData()
        current_identifier = _identifier(current_selection) if current_selection else None

        # Clear the combo box before updating:
        self.username_address_port_combo_box.clear()

        # Re-populate the combo box with updated server list:
        for key, username_address_port in self.code_drop_client.servers.items():
            string_to_display = f"{username_address_port[0]} at {key} ({username_address_port[1]}:{username_address_port[2]})"

            # Add the server to the combo box, using the identifier as the item data for easy lookup:
            self.username_address_port_combo_box.addItem(string_to_display,
                                                         username_address_port)

        # Restore the current selection by finding the item with the matching unique identifier:
        if current_identifier:
            for index in range(self.username_address_port_combo_box.count()):
                item_data = self.username_address_port_combo_box.itemData(
                    index)
                item_identifier = _identifier(item_data)
                if item_identifier == current_identifier:
                    self.username_address_port_combo_box.setCurrentIndex(
                        index)
                    break
        else:
            # If there was no selection or the selected server is no longer available, default to the first item:
            self.username_address_port_combo_box.setCurrentIndex(0)

    def send_code(self):

        # Get the selected server address and port:
        username_address_port = self.username_address_port_combo_box.currentData()

        if username_address_port:
            # Split address from port:
            username, server_address, server_port = username_address_port

            # Logging":
            aprint(
                f"Sending code to {username} at {server_address}:{server_port}.")

            # Get the filename and code:
            filename, code = self.get_code_callable()

            if filename is not None and code is not None:
                # Send message:
                self.code_drop_client.send_code_message(server_address=server_address,
                                                        server_port=server_port,
                                                        filename=filename,
                                                        code=code)
            else:
                aprint("No code to send, no code could be obtained.")
        else:
            aprint("Please select a recipient.")

        # To avoid code duplication, we call canceled to hide widget and stop discovery:
        self.canceled()


    def canceled(self):

        # Hide:
        self.hide()

        # Disable discovery worker:
        self.code_drop_client.discover_worker.is_enabled = False

        # Stop refreshing server list:
        self.stop_server_list_refresh()

    def start_server_list_refresh(self):

        # Initial refresh:
        self.update_server_list()

        # Start the timer:
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_server_list)
        self.timer.start(self.refresh_interval)

        # Ensure the timer is stopped when the widget is closed:
        self.destroyed.connect(self.stop_server_list_refresh)

    def stop_server_list_refresh(self):
        # Stop the timer:
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
            self.timer=None

    def show_send_dialog(self,
                         get_code_callable: Callable[[], Tuple[str, str]]):

        # Store the filename and code:
        self.get_code_callable = get_code_callable

        # Enable discovery worker:
        self.code_drop_client.discover_worker.is_enabled = True

        # Start refreshing server list:
        self.start_server_list_refresh()

        # show widget:
        self.show()


    def stop(self):
        # Stop refreshing server list:
        self.stop_server_list_refresh()

    def close(self):
        self.stop()
        super().close()
