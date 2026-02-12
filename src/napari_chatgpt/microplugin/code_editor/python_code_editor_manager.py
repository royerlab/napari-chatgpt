"""Manager for multiple named code editor instances with lazy creation."""

from qtpy.QtWidgets import QVBoxLayout, QWidget

from napari_chatgpt.microplugin.code_editor.python_code_editor_widget import (
    PythonCodeEditor,
)


class MultiEditorManager(QWidget):
    """Manages multiple named PythonCodeEditor instances, showing one at a time.

    Editors are created lazily on first access and cached by filename. Only
    the active editor's ``textChanged`` signal is connected to the callback.

    Attributes:
        editors: Dict mapping filenames to their PythonCodeEditor instances.
        current_editor: The currently visible editor widget, or None.
        current_editor_name: Filename of the currently visible editor, or None.
    """

    def __init__(
        self,
        on_text_modified_callback,
        editor_widget_class: type[QWidget] = PythonCodeEditor,
        parent=None,
    ):
        """Initialize the multi-editor manager.

        Args:
            on_text_modified_callback: Callable invoked when the active editor's
                text changes.
            editor_widget_class: Widget class to instantiate for each editor tab.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.on_text_modified_callback = on_text_modified_callback
        self.editor_widget_class = editor_widget_class
        self.main_layout = QVBoxLayout(self)
        self.editors = {}  # Key: filename, Value: PythonCodeEditor instance
        self.current_editor_name = None
        self.current_editor = None

    def switch_to(self, filename):
        """Switch to the editor for the given filename, creating it if needed.

        Hides the previous editor and disconnects its ``textChanged`` signal,
        then shows (and optionally creates) the editor for the specified file.

        Args:
            filename: The filename key identifying the editor to switch to.
        """

        # If we are already editing the filename, do nothing:
        if filename == self.current_editor_name:
            return

        if self.current_editor:
            # Disconnect the previous editor's textChanged signal
            self.current_editor.textChanged.disconnect(self.on_text_modified_callback)

            # Hide the previous editor:
            self.current_editor.hide()

        # If the editor for the filename does not exist, create it:
        if filename not in self.editors:
            editor = self.editor_widget_class(self)
            self.editors[filename] = editor
            self.main_layout.addWidget(editor)

        # Set the current editor to the editor for the filename:
        self.current_editor = self.editors[filename]

        # Set the current editor name to the filename:
        self.current_editor_name = filename

        # Connect the current editor's textChanged signal to the callback:
        self.current_editor.textChanged.connect(self.on_text_modified_callback)

        # Show the current editor:
        self.current_editor.show()

    def close(self):
        """Close all managed editors and then the manager widget itself."""

        # Close all the editors:
        for editor in self.editors.values():
            editor.close()

        # Close the parent widget
        super().close()
