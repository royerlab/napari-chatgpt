from qtpy.QtWidgets import QWidget, QVBoxLayout

from microplugin.code_editor.python_code_editor_widget import \
    PythonCodeEditor


class MultiEditorManager(QWidget):
    def __init__(self,
                 on_text_modified_callback,
                 editor_widget_class: type[QWidget] = PythonCodeEditor,
                 parent=None):
        super().__init__(parent)
        self.on_text_modified_callback = on_text_modified_callback
        self.editor_widget_class = editor_widget_class
        self.layout = QVBoxLayout(self)
        self.editors = {}  # Key: filename, Value: PythonCodeEditor instance
        self.current_editor_name = None
        self.current_editor = None


    def switch_to(self, filename):

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
