from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout
from arbol import aprint

from napari_chatgpt.utils.api_keys.api_key_vault import KeyVault


class APIKeyDialog(QDialog):
    def __init__(self, api_key_name: str, parent=None):
        super().__init__(parent)

        self.api_key = None

        self.key_vault = KeyVault(api_key_name)

        self.setWindowTitle(f'{api_key_name} API Key Vault')

        layout = QVBoxLayout()

        enter_new_key = not self.key_vault.is_key_present()

        if enter_new_key:
            # Create the label, text field, and button
            self.api_key_label = QLabel(f'Enter {api_key_name} API key:', self)
            self.api_key_textbox = QLineEdit(self)
            layout.addWidget(self.api_key_label)
            layout.addWidget(self.api_key_textbox)

        # Create the label, text field, and button
        passsword_label_text = 'Enter password to unlock key:' if self.key_vault.is_key_present() else 'Enter password to secure key:'
        self.password_label = QLabel(passsword_label_text, self)
        self.password_textbox = QLineEdit(self)
        if not enter_new_key:
            self.password_textbox.setEchoMode(QLineEdit.Password)

        # Add to layout:
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_textbox)



        self.button = QPushButton('Enter', self)
        # Connect the button to a slot
        self.button.clicked.connect(self.button_clicked)
        # Add to layout:
        layout.addWidget(self.button)

        self.setLayout(layout)

    def button_clicked(self):

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
            api_key = self.api_key_textbox.text()
            password = self.password_textbox.text()

            # Do something with the text (e.g. print it)
            # aprint(api_key)

            # Encrypt and store API key:
            self.key_vault.write_api_key(api_key=api_key,
                                         password=password)

            self.api_key = api_key

            # Close the dialog box
            self.accept()

    def get_api_key(self) -> str:
        api_key = self.api_key

        # For safety we delete the key in the field:
        self.api_key = None
        return api_key


def request_if_needed_api_key_dialog(api_key_name: str) -> str:
    dialog = APIKeyDialog(api_key_name=api_key_name)

    # Set the dialog box to be modal, so that it blocks interaction with the main window
    dialog.setModal(True)

    # Show the dialog box
    dialog.exec()

    # Return key:
    return dialog.get_api_key()
