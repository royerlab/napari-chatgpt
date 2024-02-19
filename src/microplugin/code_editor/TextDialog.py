# Custom dialog for displaying large amounts of text within reasonable limits
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QTextEdit, QSizePolicy, QVBoxLayout, \
    QPushButton


class TextDialog(QDialog):
    def __init__(self, title, text, icon=None,
                 parent=None):  # icon parameter is optional and can be None
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)

        # Use a QTextEdit inside the dialog to display long messages
        self.textEdit = QTextEdit()
        self.textEdit.setText(text)
        self.textEdit.setReadOnly(True)
        self.textEdit.setSizePolicy(QSizePolicy.Expanding,
                                    QSizePolicy.Expanding)

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