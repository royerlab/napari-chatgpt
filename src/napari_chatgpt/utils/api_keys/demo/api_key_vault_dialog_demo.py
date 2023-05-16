import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

from napari_chatgpt.utils.api_keys.api_key_vault_dialog import \
    request_if_needed_api_key_dialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Press me for a dialog!")
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)

    def button_clicked(self, s):
        api_key = request_if_needed_api_key_dialog('OpenAI')
        print(f"OpenAI API KEY {api_key}")


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
