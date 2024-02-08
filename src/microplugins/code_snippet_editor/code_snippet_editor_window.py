import sys
from typing import Tuple, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox


from PyQt5.QtWidgets import QApplication

from microplugins.code_snippet_editor.code_snippet_editor_widget import \
    CodeSnippetEditorWidget

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Enable high-DPI scaling
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # Use high-DPI icons

class CodeSnippetEditorWindow(QMainWindow):
    def __init__(self,
                 folder_path: str,
                 title: Optional[str] = "Python Code Snippet Editor",
                 size: Optional[Tuple[int, int]] = None,
                 *args, **kwargs):
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
        super(CodeSnippetEditorWindow, self).__init__(*args, **kwargs)
        self.codeEditorWidget = CodeSnippetEditorWidget(folder_path)
        self.setCentralWidget(self.codeEditorWidget)
        self.setWindowTitle(title)
        self.resize(size or self.codeEditorWidget.sizeHint())

    def closeEvent(self, event):
        if self.codeEditorWidget.modified:
            response = QMessageBox.question(self, "Save Changes",
                                            "You have unsaved changes. Would you like to save them before closing?",
                                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if response == QMessageBox.Yes:
                self.codeEditorWidget.save_current_file()
                event.accept()  # Proceed with the window closure
            elif response == QMessageBox.No:
                event.accept()  # Ignore changes and close
            else:
                event.ignore()  # Cancel the close event
        else:
            event.accept()  # No modifications, so just close

    # Optional: Implement changeEvent or other methods to handle focus changes
    # This example does not include focus handling as it's more complex and less common


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = CodeSnippetEditorWindow('', size=(800, 600))
    mainWindow.show()

    sys.exit(app.exec_())
