import os
import sys
from typing import Tuple, Optional

from PyQt5.QtWidgets import QApplication

from microplugins.code_snippet_editor.code_snippet_editor_window import \
    CodeSnippetEditorWindow
from napari_chatgpt.utils.configuration.app_configuration import \
    AppConfiguration


class MicroPluginMainWindow(CodeSnippetEditorWindow):
    def __init__(self,
                 size: Optional[Tuple[int, int]] = None,
                 *args, **kwargs):

        # Get configuration
        config = AppConfiguration('microplugins')

        # default folder is microplugins in the user's home directory:
        default_folder_path = '~./microplugins'

        # Get the folder path:
        folder_path = config.get('folder', default_folder_path)

        # Make sure that the folder exists:
        folder_path = os.path.expanduser(folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        super(MicroPluginMainWindow, self).__init__(folder_path=folder_path,
                                                    title="Micro-Plugins Editor",
                                                    size=size,
                                                    *args,
                                                    **kwargs)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = MicroPluginMainWindow()
    mainWindow.show()

    sys.exit(app.exec_())

