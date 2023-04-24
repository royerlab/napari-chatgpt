import sys

from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication

from napari_chatgpt.utils.browser_widget import BrowserWindow

app = QApplication(sys.argv)

window = BrowserWindow()

window.show()

loop = QEventLoop()
window.destroyed.connect(loop.quit)
loop.exec()  # wait ...
print('finished')
