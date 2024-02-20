from arbol import aprint
from qtpy.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

from napari_chatgpt.utils.api_keys.api_key_vault import KeyVault


class APIKeyDialog(QDialog):

    def __init__(self, api_key_name: str, parent=None):
        super().__init__(parent)

        # Set the dialog box to be modal, so that it blocks interaction with the main window
        self.setModal(True)

        self.api_key_name = api_key_name

        self.api_key = None

        self.key_vault = KeyVault(api_key_name)

        self.setWindowTitle(f'{api_key_name} API Key Vault')

        self._populate_layout()

    def _clear_layout(self):

        layout = self.layout()

        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _populate_layout(self):

        layout = self.layout()

        if layout is None:
            layout = QVBoxLayout()
            self.setLayout(layout)

        enter_new_key = not self.key_vault.is_key_present()
        if enter_new_key:
            # Create the label, text field, and button
            self.api_key_label = QLabel(f'Enter {self.api_key_name} API key:', self)
            self.api_key_textbox = QLineEdit(self)

            # Add tooltip text:
            self.api_key_textbox.setToolTip(f'Enter your {self.api_key_name} API key here.\n'
                                            f'You will not need to remember this API key,\n'
                                            f'only the shorter password you enter below.')

            # Add to layout:
            layout.addWidget(self.api_key_label)
            layout.addWidget(self.api_key_textbox)

        # Create the label, text field, and button
        passsword_label_text = 'Enter password to unlock key:' if self.key_vault.is_key_present() else 'Enter password to secure key:'
        self.password_label = QLabel(passsword_label_text, self)
        self.password_textbox = QLineEdit(self)
        self.password_textbox.setEchoMode(QLineEdit.Password)
        # Set tooltip text:
        if enter_new_key:
            self.password_textbox.setToolTip('Enter a password to secure your API key.\n'
                                             'You will need to remember this password\n'
                                             'to give Omega access your API key.')
        else:
            self.password_textbox.setToolTip('Enter the password you used to secure your API key.\n')

        # Add to layout:
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_textbox)

        # Create the button:
        self.button = QPushButton('Enter', self)

        # Connect the button to a slot
        self.button.clicked.connect(self.enter_button_clicked)

        # Add Button to layout:
        layout.addWidget(self.button)

        if not enter_new_key:

            # Add a button to ignore the dialog::
            self.cancel_button = QPushButton('Continue without API key', self)
            # Set tooltip text:
            self.cancel_button.setToolTip('Click here to continue without setting the API key.\n'
                                          'You won`t be able to dialog with Omega. However,\n'
                                          'some features such as the code editor will be available\n'
                                          'but without any of the AI features.')

            # Connect the button to a slot
            self.cancel_button.clicked.connect(self.accept)

            # Add to layout:
            layout.addWidget(self.cancel_button)

            # Add a button to clear the key:
            self.reset_button = QPushButton('Reset API Key and Password', self)
            self.reset_button.setStyleSheet("QPushButton { color: #8B0000; }")
            # Set tooltip text:
            self.reset_button.setToolTip('Click here to reset the API key and password.\n'
                                        'You will need to enter a new API key and password.')

            # Connect the button to a slot
            self.reset_button.clicked.connect(self.reset_button_clicked)

            # Add to layout:
            layout.addWidget(self.reset_button)




        return layout

    def enter_button_clicked(self):

        if self.key_vault.is_key_present():
            from cryptography.fernet import InvalidToken
            try:
                password = self.password_textbox.text()

                # Decrypt API key:
                self.api_key = self.key_vault.read_api_key(password=password)

                # Close the dialog box
                self.accept()
            except InvalidToken:
                aprint("Invalid password!")

        else:
            # Get the text from the text field
            api_key = self.api_key_textbox.text().strip()
            password = self.password_textbox.text().strip()

            # Check if the text is empty or malformed or if password is empty:
            if not api_key or not password:
                aprint("Please enter a valid API key and password.")
                return

            # Encrypt and store API key:
            self.key_vault.write_api_key(api_key=api_key,
                                         password=password)

            self.api_key = api_key

            # Close the dialog box
            self.accept()

    def reset_button_clicked(self):

        # Clear clear key:
        self.key_vault.clear_key()

        # Delete the key:
        self.api_key = None

        # Clear layout:
        self._clear_layout()

        # Repopulate layout:
        self._populate_layout()


    def get_api_key(self) -> str:

        # get API key:
        api_key = self.api_key

        # For safety we delete the key in the field:
        self.api_key = None
        return api_key

_already_asked_api_key = {}

def request_if_needed_api_key_dialog(api_key_name: str) -> str:

    if api_key_name in _already_asked_api_key:
        return None

    dialog = APIKeyDialog(api_key_name=api_key_name)

    # Show the dialog box
    dialog.exec()

    _already_asked_api_key[api_key_name] = True

    # Return key:
    return dialog.get_api_key()
