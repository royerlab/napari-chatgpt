"""Main window for the MicroPlugin code editor integrated with napari.

Provides a singleton-based code snippet editor window that inherits napari's
stylesheet and allows users to create, edit, and manage micro-plugins
(small code snippets) from within the napari viewer.
"""

import os
import sys

from arbol import aprint
from napari._qt.qt_resources import get_current_stylesheet
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from napari_chatgpt.microplugin.code_editor.code_snippet_editor_window import (
    CodeSnippetEditorWindow,
)


class MicroPluginMainWindow(CodeSnippetEditorWindow):
    """Singleton main window for editing and managing napari micro-plugins.

    Extends CodeSnippetEditorWindow with napari integration, including
    stylesheet inheritance, persistent storage of code snippets, and
    network-based code sharing. Uses a singleton pattern so only one
    instance exists per application.

    Attributes:
        llm_model_name: Name of the LLM model used for AI-assisted editing.
    """

    _singleton_pattern_active = True
    _singleton_instance = None
    _singleton_instance_initialized = False

    def __new__(cls, *args, **kwargs):

        if cls._singleton_pattern_active:
            if cls._singleton_instance is None:
                # Call __new__ of the parent class and save the instance:
                cls._singleton_instance = super().__new__(cls)

            return cls._singleton_instance

        else:
            # We still want the last instance to be recorded:
            cls._singleton_instance = super().__new__(cls)
            return cls._singleton_instance

    def __init__(
        self,
        napari_viewer,
        folder_path: str | None = None,
        size: tuple[int, int] | None = None,
        parent=None,
        *args,
        **kwargs,
    ):
        """Initialize the MicroPlugin main window.

        Args:
            napari_viewer: The napari viewer instance to integrate with.
            folder_path: Directory for storing micro-plugin files. Defaults
                to ``~/microplugins`` or the configured path.
            size: Optional ``(width, height)`` tuple for the window.
            parent: Optional parent Qt widget.
        """

        # If the singleton instance is already initialized, just return it:
        if (
            MicroPluginMainWindow._singleton_pattern_active
            and MicroPluginMainWindow._singleton_instance_initialized
        ):
            return

        if folder_path is None:
            # Local import to avoid circular import:
            from napari_chatgpt.utils.configuration.app_configuration import (
                AppConfiguration,
            )

            # Get configuration
            config = AppConfiguration("microplugins")

            # default folder is microplugins in the user's home directory:
            default_folder_path = "~/microplugins"

            # Get the folder path:
            folder_path = config.get("folder", default_folder_path)

        # Make sure that the folder exists:
        folder_path = os.path.expanduser(folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        super().__init__(
            folder_path=folder_path,
            title="Micro-Plugins Editor",
            size=size,
            variables={"viewer": napari_viewer},
            parent=parent,
            *args,
            **kwargs,
        )

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
            self.setGeometry(
                int(left), int(top), int(desired_width), int(desired_height)
            )
        except Exception as e:
            aprint(f"Error setting window size and position: {e}")
            import traceback

            traceback.print_exc()

        # LLM settings:
        self.llm_model_name = None

        # Set the instance as initialized:
        MicroPluginMainWindow._singleton_instance_initialized = True

    @staticmethod
    def add_snippet(filename: str, code: str | None = None):
        """Add a new code snippet file to the editor.

        Creates a new file in the micro-plugins folder with the given
        filename and optional code content. If the file already exists,
        a ``_new_from_omega`` suffix is appended.

        Args:
            filename: Name for the new snippet file.
            code: Optional Python source code for the snippet.
        """

        # Create a new file with the given code:
        MicroPluginMainWindow._singleton_instance.code_editor_widget.new_file(
            filename=filename, code=code, postfix_if_exists="_new_from_omega"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = MicroPluginMainWindow()
    mainWindow.show()

    sys.exit(app.exec_())
