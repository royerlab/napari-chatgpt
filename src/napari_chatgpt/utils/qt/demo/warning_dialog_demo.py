import sys

from qtpy.QtWidgets import QApplication

from napari_chatgpt.utils.qt.warning_dialog import show_warning_dialog

# Example usage
if __name__ == '__main__':
    app = QApplication(sys.argv)
    html_message = "There is an issue. Please visit <a href='https://example.com'>this link</a> for more information."
    show_warning_dialog(html_message)
    sys.exit(app.exec_())