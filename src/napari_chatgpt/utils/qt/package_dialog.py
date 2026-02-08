from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QDialog,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from napari_chatgpt.utils.qt.qt_app import get_or_create_qt_app, run_on_main_thread


class PackageDialog(QDialog):
    def __init__(self, packages, parent=None):
        super().__init__(parent, flags=Qt.WindowStaysOnTopHint)
        self.packages = packages
        self.user_response: bool | None = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Placeholder for explanatory message
        message_label = QLabel(
            "The following packages need to be installed. \n"
            "Please review the list and accept or refuse. \n"
            "If you refuse Omega might not be able to fulfill the task.",
            self,
        )

        layout.addWidget(message_label)

        # List widget for packages
        self.listWidget = QListWidget(self)
        self.listWidget.setSelectionMode(QListWidget.NoSelection)  # Disable selection
        self.listWidget.addItems(self.packages)
        layout.addWidget(self.listWidget)

        # Setting size policy and maximum visible items
        self.listWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.listWidget.setMaximumHeight(
            self.listWidget.sizeHintForRow(0) * 12 + 2 * self.listWidget.frameWidth()
        )

        # Yes and No buttons
        yes_btn = QPushButton("Install packages", self)
        no_btn = QPushButton("Do not install packages", self)
        yes_btn.clicked.connect(self.accept)
        no_btn.clicked.connect(self.reject)
        layout.addWidget(yes_btn)
        layout.addWidget(no_btn)

        self.setLayout(layout)

    def accept(self):
        self.user_response = True
        super().accept()

    def reject(self):
        self.user_response = False
        super().reject()


def install_packages_dialog(packages, app=None) -> bool:
    if not app:
        app = get_or_create_qt_app()
    dialog = PackageDialog(packages)
    dialog.exec_()
    return dialog.user_response


def install_packages_dialog_threadsafe(packages) -> bool:
    """Show the install-packages dialog on the Qt main thread and block until
    the user responds.  Safe to call from any worker thread."""
    from queue import Empty, Queue

    result_queue = Queue(maxsize=1)

    def _show_dialog():
        result = install_packages_dialog(packages)
        result_queue.put(result)

    run_on_main_thread(_show_dialog)
    try:
        return result_queue.get(timeout=300)
    except Empty:
        return False
