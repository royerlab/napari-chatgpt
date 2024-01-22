import sys
from typing import Callable

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def get_or_create_qt_app():
    # Check if there is already a QApplication instance running
    if not QApplication.instance():
        # If not, create a new QApplication instance
        app = QApplication(sys.argv)
    else:
        # If there is, use the existing QApplication instance
        app = QApplication.instance()

    return app




def run_on_main_thread(func: Callable):
    QTimer.singleShot(0, func)