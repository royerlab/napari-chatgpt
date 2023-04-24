from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow


class BrowserWindow(QMainWindow):

    def __init__(self, url: str = 'http://www.google.com', *args, **kwargs):
        super(BrowserWindow, self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)
        self.show()

# app = QApplication(sys.argv)
# window = MainWindow()
#
# app.exec_()
