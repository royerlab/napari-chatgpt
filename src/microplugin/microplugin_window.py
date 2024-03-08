import os
import sys
from typing import Tuple, Optional

from arbol import aprint
from napari._qt.qt_resources import get_current_stylesheet
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from microplugin.code_editor.code_snippet_editor_window import \
    CodeSnippetEditorWindow


class MicroPluginMainWindow(CodeSnippetEditorWindow):

    _singleton_pattern_active = True
    _singleton_instance = None
    _singleton_instance_initialized = False

    def __new__(cls, *args, **kwargs):

        if cls._singleton_pattern_active:
            if cls._singleton_instance is None:

                # Call __new__ of the parent class and save the instance:
                cls._singleton_instance = super(MicroPluginMainWindow, cls).__new__(cls)

            return cls._singleton_instance

        else:
            # We still want the last instance to be recorded:
            cls._singleton_instance = super().__new__(cls)
            return cls._singleton_instance


    def __init__(self,
                 napari_viewer,
                 folder_path: Optional[str] = None,
                 size: Optional[Tuple[int, int]] = None,
                 parent=None,
                 *args,
                 **kwargs):

        # If the singleton instance is already initialized, just return it:
        if MicroPluginMainWindow._singleton_pattern_active and MicroPluginMainWindow._singleton_instance_initialized:
            return

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

        # Set window size and position to be centered and occupy specified screen space
        try:
            screen = QApplication.primaryScreen().geometry()
            desired_width = screen.width() * 0.5  # 50% of screen width
            desired_height = screen.height() * 0.6  # 60% of screen height
            left = (screen.width() - desired_width) / 2
            top = (screen.height() - desired_height) / 2
            self.setGeometry(int(left), int(top), int(desired_width), int(desired_height))
        except Exception as e:
            aprint(f'Error setting window size and position: {e}')
            import traceback
            traceback.print_exc()

        # LLM settings:
        self.llm_model_name = None

        # Set the instance as initialized:
        MicroPluginMainWindow._singleton_instance_initialized = True



    @staticmethod
    def add_snippet(filename: str,
                    code: Optional[str] = None):

        # Create a new file with the given code:
        MicroPluginMainWindow._singleton_instance.code_editor_widget.new_file(filename=filename, code=code, postfix_if_exists='_new_from_omega')

if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = MicroPluginMainWindow()
    mainWindow.show()

    sys.exit(app.exec_())
