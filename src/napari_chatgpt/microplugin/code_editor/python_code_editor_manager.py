from qtpy.QtWidgets import QWidget, QVBoxLayout

from napari_chatgpt.microplugin.code_editor.python_code_editor_widget import (
    PythonCodeEditor,
)


class MultiEditorManager(QWidget):
    def __init__(
        self,
        on_text_modified_callback,
        editor_widget_class: type[QWidget] = PythonCodeEditor,
        parent=None,
    ):
        """
        Initialize the MultiEditorManager with a text modification callback, an optional editor widget class, and an optional parent widget.
        
        Parameters:
            on_text_modified_callback: Callback function to be invoked when the text in any editor is modified.
            editor_widget_class (type[QWidget], optional): The class to use for creating editor widgets. Defaults to PythonCodeEditor.
            parent (QWidget, optional): The parent widget for this manager.
        """
        super().__init__(parent)
        self.on_text_modified_callback = on_text_modified_callback
        self.editor_widget_class = editor_widget_class
        self.layout = QVBoxLayout(self)
        self.editors = {}  # Key: filename, Value: PythonCodeEditor instance
        self.current_editor_name = None
        self.current_editor = None

    def switch_to(self, filename):

        # If we are already editing the filename, do nothing:
        """
        Switch the active editor to the one associated with the specified filename.
        
        If an editor for the given filename does not exist, it is created and added to the layout. The method updates internal references, manages signal connections for text modification callbacks, and ensures only the selected editor is visible.
        """
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
            self.layout.addWidget(editor)

        # Set the current editor to the editor for the filename:
        self.current_editor = self.editors[filename]

        # Set the current editor name to the filename:
        self.current_editor_name = filename

        # Connect the current editor's textChanged signal to the callback:
        self.current_editor.textChanged.connect(self.on_text_modified_callback)

        # Show the current editor:
        self.current_editor.show()

    def close(self):

        # Close all the editors:
        for editor in self.editors.values():
            editor.close()

        # Close the parent widget
        super().close()
