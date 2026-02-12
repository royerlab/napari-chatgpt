"""Read-only console output widget for displaying script execution results."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ConsoleWidget(QWidget):
    """A popup console widget that displays formatted info and error messages.

    Messages are displayed with color coding (green for info, red for errors)
    and the widget auto-shows when a message is appended. Includes close and
    clear buttons.
    """

    def __init__(self, margin: int = 0, icon_size: int = 20, parent=None):
        """Initialize the console widget.

        Args:
            margin: Layout margin in pixels.
            icon_size: Width and height of the close/clear buttons in pixels.
            parent: Parent widget.
        """

        super().__init__(parent=parent)

        # This helps in auto-hiding when losing focus:
        self.setWindowFlags(Qt.Popup)

        # Initialize the UI
        self.initUI(margin=margin, icon_size=icon_size)

    def initUI(self, margin: int, icon_size: int):
        """Build the console UI with close/clear buttons and a read-only text area."""

        # Main layout
        self.main_layout = QVBoxLayout()

        # Top bar layout for the close and clear buttons
        self.topBarLayout = QHBoxLayout()

        # Set spacing between widgets in the layout to a smaller value
        self.topBarLayout.setSpacing(1)  # Adjust this value as needed

        # Close and clear buttons
        self.closeButton = QPushButton("X")
        self.clearButton = QPushButton("C")

        # Set the size of the buttons
        self.closeButton.setFixedSize(icon_size, icon_size)  # Make the button small
        self.clearButton.setFixedSize(icon_size, icon_size)  # Make the button small

        # Connect the close button to the hide method
        self.closeButton.clicked.connect(self.hide)
        self.clearButton.clicked.connect(self.clear_console)  # Connect clear button

        # Add a spacer to push the close button to the right
        self.topBarLayout.addStretch()
        self.topBarLayout.addWidget(self.clearButton)  # Add clear button
        self.topBarLayout.addWidget(self.closeButton)

        # Create a read-only QTextEdit widget to act as the console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setLineWrapMode(QTextEdit.NoWrap)

        # Add the top bar layout and the console output to the main layout
        self.main_layout.addLayout(self.topBarLayout)
        self.main_layout.addWidget(self.console_output)

        # Set the layout margins:
        self.main_layout.setContentsMargins(margin, margin, margin, margin)

        # Set the layout to the widget
        self.setLayout(self.main_layout)

        # Hide the widget initially:
        self.hide()

    def append_message(self, message: str, message_type: str = "info"):
        """Append a message to the console output and show the widget.

        Args:
            message: The message text to append. Whitespace is preserved
                using HTML non-breaking spaces.
            message_type: Message category for color formatting. ``'info'``
                renders green, ``'error'`` renders red.
        """

        # Clean the message:
        message = message.strip()

        # if the message is empty, do nothing:
        if len(message) == 0:
            return

        # Replace '\n' with '<br>' to display newlines in the QTextEdit:
        message = message.replace("\n", "<br>")

        # Replace '\t' with '&nbsp;&nbsp;&nbsp;&nbsp;' to display tabs in the QTextEdit:
        message = message.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")

        # Replace ' ' with '&nbsp;' to display spaces in the QTextEdit:
        message = message.replace(" ", "&nbsp;")

        if message_type == "error":
            message = f"<span style='color: red;'>{message}</span>"
        elif message_type == "info":
            message = f"<span style='color: green;'>{message}</span>"

        # Append the message to the console
        self.console_output.append(message)

        # show the widget:
        self.show()

    def clear_console(self):
        """Clear all messages from the console output."""
        self.console_output.clear()


# Example usage
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    consoleWidget = ConsoleWidget()
    consoleWidget.show()
    consoleWidget.append_message("This is an info message.", "info")
    consoleWidget.append_message("This is an error message.", "error")

    sys.exit(app.exec_())
