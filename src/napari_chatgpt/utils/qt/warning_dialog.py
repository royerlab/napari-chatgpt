from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMessageBox


def show_warning_dialog(html_message: str) -> int:
    """
    Display a modal warning dialog with an HTML-formatted message.
    
    Parameters:
        html_message (str): The message to display, interpreted as HTML.
    
    Returns:
        int: The result code from the dialog execution.
    """
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Warning)
    dialog.setText(html_message)
    dialog.setWindowTitle("Warning")
    dialog.setTextFormat(
        Qt.TextFormat.RichText
    )  # Set text format to RichText to interpret HTML
    dialog.setStandardButtons(QMessageBox.Ok)
    return dialog.exec_()
