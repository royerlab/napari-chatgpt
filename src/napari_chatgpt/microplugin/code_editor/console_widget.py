from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QApplication,
    QHBoxLayout,
    QPushButton,
)


class ConsoleWidget(QWidget):
    def __init__(self, margin: int = 0, icon_size: int = 20, parent=None):

        """
        Initialize the ConsoleWidget with optional margin and icon size.
        
        Parameters:
            margin (int, optional): Margin size for the widget layout. Defaults to 0.
            icon_size (int, optional): Size of the control buttons. Defaults to 20.
        """
        super().__init__(parent=parent)

        # This helps in auto-hiding when losing focus:
        self.setWindowFlags(Qt.Popup)

        # Initialize the UI
        self.initUI(margin=margin, icon_size=icon_size)

    def initUI(self, margin: int, icon_size: int):

        # Main layout
        """
        Set up the user interface for the console widget, including control buttons and the console output area.
        
        Parameters:
            margin (int): The margin size to apply around the widget's layout.
            icon_size (int): The size (width and height) of the control buttons in pixels.
        """
        self.layout = QVBoxLayout()

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
        self.layout.addLayout(self.topBarLayout)
        self.layout.addWidget(self.console_output)

        # Set the layout margins:
        self.layout.setContentsMargins(margin, margin, margin, margin)

        # Set the layout to the widget
        self.setLayout(self.layout)

        # Hide the widget initially:
        self.hide()

    def append_message(self, message: str, message_type: str = "info"):
        """
        Appends a formatted message to the console output, displaying it in a color based on message type.
        
        Parameters:
            message (str): The message to display in the console.
            message_type (str): The type of message, determining its color ("info" for green, "error" for red). Defaults to "info".
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
        """
        Clear the console output.
        """
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
