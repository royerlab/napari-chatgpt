import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox

def show_warning_dialog(html_message):
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Warning)
    dialog.setText(html_message)
    dialog.setWindowTitle("Warning")
    dialog.setTextFormat(Qt.TextFormat.RichText)  # Set text format to RichText to interpret HTML
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()

# Example usage
if __name__ == '__main__':
    app = QApplication(sys.argv)
    html_message = "There is an issue. Please visit <a href='https://example.com'>this link</a> for more information."
    show_warning_dialog(html_message)
    sys.exit(app.exec_())