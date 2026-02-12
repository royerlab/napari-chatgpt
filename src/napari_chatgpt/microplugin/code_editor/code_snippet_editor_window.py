"""Standalone window wrapping the CodeSnippetEditorWidget."""

import sys

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QMainWindow

from napari_chatgpt.microplugin.code_editor.code_snippet_editor_widget import (
    CodeSnippetEditorWidget,
)

# Enable High DPI display with PyQt5
if hasattr(Qt, "AA_UseHighDpiPixmaps"):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
if hasattr(Qt, "AA_EnableHighDpiScaling"):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


class CodeSnippetEditorWindow(QMainWindow):
    """QMainWindow hosting a CodeSnippetEditorWidget.

    The window title includes the folder path, hostname, and CodeDrop server
    port for easy identification when sharing code between peers.

    Attributes:
        code_editor_widget: The embedded CodeSnippetEditorWidget instance.
    """

    def __init__(
        self,
        folder_path: str,
        title: str | None = "Python Code Snippet Editor",
        size: tuple[int, int] | None = None,
        variables: dict | None = None,
        parent=None,
        *args,
        **kwargs,
    ):
        """Initialize the editor window.

        Args:
            folder_path: Path to the folder containing Python code snippets.
            title: Window title prefix.
            size: Optional ``(width, height)`` tuple for the initial window size.
            variables: Variables injected when executing snippets.
            parent: Parent widget.
            *args: Additional positional arguments for QMainWindow.
            **kwargs: Additional keyword arguments for QMainWindow.
        """
        super().__init__(parent=parent, *args, **kwargs)

        # Create the code snippet editor widget:
        self.code_editor_widget = CodeSnippetEditorWidget(
            folder_path, variables=variables, parent=self
        )
        self.setCentralWidget(self.code_editor_widget)

        # get this machine's hostname:
        server_hostname = self.code_editor_widget.server.server_hostname

        # Get the server port:
        server_port = self.code_editor_widget.server.server_port

        # Shorten the folder path to the last two directories:
        splitted_folder_path = folder_path.split("/")
        if len(splitted_folder_path) > 2:
            folder_path = "..." + "/".join(splitted_folder_path[-2:])

        # Set the window title:
        self.setWindowTitle(
            f"{title} - {folder_path} - {server_hostname}:{server_port}"
        )

        # Set the window size:
        self.resize(size or self.code_editor_widget.sizeHint())

    def close(self):
        """Close the editor widget and then the window."""
        self.code_editor_widget.close()
        super().close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = CodeSnippetEditorWindow("", size=(800, 600))
    mainWindow.show()

    sys.exit(app.exec_())
