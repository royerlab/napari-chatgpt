from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMessageBox

from napari_chatgpt.utils.configuration.app_configuration import AppConfiguration


def show_one_time_disclaimer_dialog(
    html_message: str, message_title: str = "Disclaimer", app_name: str = "omega"
) -> int:
    """
    Display a one-time disclaimer dialog with an HTML-formatted message.
    
    If the disclaimer has already been acknowledged, the dialog is not shown and an OK response is returned. Otherwise, the dialog is displayed, and acknowledgment is recorded for future runs.
    
    Parameters:
        html_message (str): The HTML content to display in the dialog.
        message_title (str, optional): The title of the dialog window. Defaults to "Disclaimer".
        app_name (str, optional): The application name used for configuration. Defaults to "omega".
    
    Returns:
        int: The response code from the dialog interaction (typically QMessageBox.Ok).
    """

    # Get app configuration:
    config = AppConfiguration(app_name)

    # Check if the disclaimer has been shown before:
    if config.get("disclaimer_shown_and_acknowledged"):
        return QMessageBox.Ok

    # Prepare the dialog:
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Information)
    dialog.setText(html_message)
    dialog.setWindowTitle(message_title)
    dialog.setTextFormat(
        Qt.TextFormat.RichText
    )  # Set text format to RichText to interpret HTML
    dialog.setStandardButtons(QMessageBox.Ok)

    # Show the dialog and get the response:
    response = dialog.exec_()

    if response == QMessageBox.Ok:
        # Saving response:
        config["disclaimer_shown_and_acknowledged"] = True

    return response
