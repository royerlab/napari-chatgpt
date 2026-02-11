"""Modal dialog for displaying scrollable read-only text content."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QPushButton, QSizePolicy, QTextEdit, QVBoxLayout


class TextDialog(QDialog):
    """A modal dialog that displays a large block of text in a scrollable view.

    Contains a read-only QTextEdit for the message content and an OK button
    to close the dialog. Optionally displays a window icon.
    """

    def __init__(self, title, text, icon=None, parent=None):
        """Initialize the text dialog.

        Args:
            title: The window title.
            text: The text content to display.
            icon: Optional QIcon to set as the window icon.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)

        # Use a QTextEdit inside the dialog to display long messages
        self.textEdit = QTextEdit()
        self.textEdit.setText(text)
        self.textEdit.setReadOnly(True)
        self.textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # "OK" button to close the dialog
        self.okButton = QPushButton("OK")

        # Connect the button's clicked signal to the dialog's close slot:
        self.okButton.clicked.connect(self.close)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)

        # Add the button to the layout, aligned at the center
        layout.addWidget(self.okButton, 0, Qt.AlignCenter)
        self.setLayout(layout)

        # Set the window icon if an icon is provided
        if icon is not None:
            self.setWindowIcon(icon)
