import os
import sys
from typing import Tuple, Optional

from napari._qt.qt_resources import get_current_stylesheet
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from microplugin.code_editor.code_snippet_editor_window import \
    CodeSnippetEditorWindow


class MicroPluginMainWindow(CodeSnippetEditorWindow):

    _singleton_pattern_active = True
    _singleton_instance = None

    def __new__(cls, *args, **kwargs):

        if cls._singleton_pattern_active:
            if cls._singleton_instance is None:

                # Call __new__ of the parent class and save the instance:
                cls._singleton_instance = super(MicroPluginMainWindow, cls).__new__(cls)

            return cls._singleton_instance

        else:
            # We still want the last instance to be recorded:
            cls._singleton_instance = super().__new__(cls)
            return


    def __init__(self,
                 napari_viewer,
                 folder_path: Optional[str] = None,
                 size: Optional[Tuple[int, int]] = None,
                 parent=None,
                 *args,
                 **kwargs):

        if folder_path is None:

            # Local import to avoid circular import:
            from napari_chatgpt.utils.configuration.app_configuration import \
                AppConfiguration

            # Get configuration
            config = AppConfiguration('microplugins')

            # default folder is microplugins in the user's home directory:
            default_folder_path = '~/microplugins'

            # Get the folder path:
            folder_path = config.get('folder', default_folder_path)

        # Make sure that the folder exists:
        folder_path = os.path.expanduser(folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        super(MicroPluginMainWindow, self).__init__(folder_path=folder_path,
                                                    title="Micro-Plugins Editor",
                                                    size=size,
                                                    variables={'viewer':napari_viewer},
                                                    parent=parent,
                                                    *args,
                                                    **kwargs)

        # Disable discovery worker until we send:
        self.code_editor_widget.client.discover_worker.is_enabled = False

        # Make sure that when user closes the window, it just hides the window, it does not really close it:
        self.setAttribute(Qt.WA_DeleteOnClose, False)

        # Get current stylesheet from napari:
        current_style = get_current_stylesheet()
        self.setStyleSheet(current_style)

        # LLM settings:
        self.llm_model_name = None



    @staticmethod
    def add_snippet(filename: str,
                    code: Optional[str] = None):

        # Create a new file with the given code:
        MicroPluginMainWindow._singleton_instance.code_editor_widget.new_file(filename=filename, code=code, postfix_if_exists='new_from_omega')

if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = MicroPluginMainWindow()
    mainWindow.show()

    sys.exit(app.exec_())
