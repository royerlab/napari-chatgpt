from typing import Optional

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QSizePolicy,
)

from napari_chatgpt.utils.qt.qt_app import get_or_create_qt_app, run_on_main_thread


class PackageDialog(QDialog):
    def __init__(self, packages, parent=None):
        super().__init__(parent, flags=Qt.WindowStaysOnTopHint)
        self.packages = packages
        self.user_response: Optional[bool] = None
        self.initUI()

    def initUI(self):
        """
        Initialize the dialog's user interface with a message, a non-selectable list of packages, and action buttons for user response.
        
        Displays an explanatory message, a list of packages to be installed, and "Install packages" and "Do not install packages" buttons for user interaction.
        """
        layout = QVBoxLayout(self)

        # Placeholder for explanatory message
        message_label = QLabel(
            "The following packages need to be installed. \n"
            "Please review the list and accept or refuse. \n"
            "If you refuse Omega might not be able to fullfill the task.",
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
        """
        Handle the rejection of the dialog by recording a negative user response and closing the dialog.
        """
        self.user_response = False
        super().reject()


def install_packages_dialog(packages, app=None) -> bool:
    """
    Display a modal dialog prompting the user to confirm installation of the specified packages.
    
    Parameters:
        packages (list): List of package names to present for installation.
    
    Returns:
        bool or None: True if the user accepts installation, False if declined, or None if the dialog is closed without a response.
    """
    if not app:
        app = get_or_create_qt_app()
    dialog = PackageDialog(packages)
    dialog.exec_()
    return dialog.user_response


def install_packages_dialog_threadsafe(packages):
    # Call the dialog on the main thread:
    """
    Display a package installation dialog on the main Qt thread in a thread-safe manner.
    
    This function ensures that the dialog prompting the user to install the specified packages is executed on the main Qt thread, which is required for GUI operations in Qt-based applications.
    """
    run_on_main_thread(lambda: install_packages_dialog(packages))
