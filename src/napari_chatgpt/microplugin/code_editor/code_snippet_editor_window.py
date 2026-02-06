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
        """
        Create a main window for the Python code snippet editor.

        Parameters
        ----------
        folder_path : str
            The path to the folder containing the Python code snippets.

        args : list
            Positional arguments to pass to the parent class.

        kwargs : dict
            Keyword arguments to pass to the parent class.

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
        self.code_editor_widget.close()
        super().close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = CodeSnippetEditorWindow("", size=(800, 600))
    mainWindow.show()

    sys.exit(app.exec_())
