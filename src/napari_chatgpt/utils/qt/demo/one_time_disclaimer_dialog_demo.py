import sys

from arbol import aprint
from qtpy.QtWidgets import QApplication

from napari_chatgpt.utils.qt.one_time_disclaimer_dialog import \
    show_one_time_disclaimer_dialog

# Example usage
if __name__ == '__main__':
    app = QApplication(sys.argv)
    html_message = "There are some things you should know, and acknowledge. Please visit <a href='https://example.com'>this link</a> for more information."
    response = show_one_time_disclaimer_dialog(html_message, app_name='test')
    aprint(response)
    sys.exit(app.exec_())