import sys
from typing import Callable

from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication


def get_or_create_qt_app():
    # Check if there is already a QApplication instance running
    """
    Return the existing QApplication instance or create one if none exists.
    
    Returns:
        QApplication: The current or newly created QApplication instance.
    """
    if not QApplication.instance():
        # If not, create a new QApplication instance
        app = QApplication(sys.argv)
    else:
        # If there is, use the existing QApplication instance
        app = QApplication.instance()

    return app


def run_on_main_thread(func: Callable):
    """
    Schedule a callable to be executed on the Qt main thread.
    
    Parameters:
        func (Callable): The function to execute on the main thread.
    """
    QTimer.singleShot(0, func)
