"""Helpers for obtaining a QApplication and scheduling work on the Qt main thread."""

import sys
from collections.abc import Callable

from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication


def get_or_create_qt_app():
    """Return the existing ``QApplication`` instance, or create one if needed."""
    # Check if there is already a QApplication instance running
    if not QApplication.instance():
        # If not, create a new QApplication instance
        app = QApplication(sys.argv)
    else:
        # If there is, use the existing QApplication instance
        app = QApplication.instance()

    return app


def run_on_main_thread(func: Callable):
    """Schedule *func* to run on the Qt main (GUI) thread via a zero-delay timer."""
    QTimer.singleShot(0, func)
