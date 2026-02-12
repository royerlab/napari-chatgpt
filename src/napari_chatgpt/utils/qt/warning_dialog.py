"""Simple Qt warning dialog that displays an HTML-formatted message."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMessageBox


def show_warning_dialog(html_message: str) -> int:
    """Show a warning dialog with a message in HTML format.

    Args:
        html_message: The message to display in HTML format.

    Returns:
        The ``QMessageBox`` button code (e.g. ``QMessageBox.Ok``).
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
