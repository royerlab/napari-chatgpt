from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QComboBox
from PyQt5.QtCore import QTimer
import sys

from microplugins.network.code_drop_client import CodeDropClient


# Assuming CodeDropClient is already implemented and available
# from your_code_drop_client_module import CodeDropClient

class CodeDropClientWidget(QWidget):
    def __init__(self, code_drop_client):
        super().__init__()
        self.code_drop_client = code_drop_client
        self.initUI()
        self.startServerListRefresh()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Server selection dropdown
        self.serverComboBox = QComboBox()
        self.layout.addWidget(self.serverComboBox)

        # Message input field
        self.messageLineEdit = QLineEdit()
        self.messageLineEdit.setPlaceholderText("Enter your message here...")
        self.layout.addWidget(self.messageLineEdit)

        # Send message button
        self.sendButton = QPushButton('Send')
        self.sendButton.clicked.connect(self.sendMessage)
        self.layout.addWidget(self.sendButton)

        self.setWindowTitle("Code Drop Client")

    def updateServerDropdown(self):
        current_servers = {self.serverComboBox.itemData(i): self.serverComboBox.itemText(i) for i in range(self.serverComboBox.count())}
        new_servers = {address_and_port: f"{name} ({address_and_port})" for name, address_and_port in self.code_drop_client.servers.items()}

        # Update if there are new servers or changes
        if current_servers != new_servers:
            self.serverComboBox.clear()
            self.serverComboBox.addItem("Select a server", None)  # Placeholder for no selection
            for server_address, server_name in new_servers.items():
                self.serverComboBox.addItem(server_name, server_address)

    def sendMessage(self):
        server_address = self.serverComboBox.currentData()
        message = self.messageLineEdit.text().strip()
        if server_address and message:
            self.code_drop_client.send_message(server_address, message)
            self.messageLineEdit.clear()
        else:
            print("Please select a server and enter a message.")

    def startServerListRefresh(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateServerDropdown)
        self.timer.start(5000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Initialize your CodeDropClient here with the appropriate multicast group and server port
    multicast_group = ('224.1.1.1', 5007)
    server_port = 5008
    code_drop_client = CodeDropClient(multicast_group, server_port)
    code_drop_client.start_discovering()

    client_widget = CodeDropClientWidget(code_drop_client)
    client_widget.show()

    sys.exit(app.exec_())
    print(client_widget)
