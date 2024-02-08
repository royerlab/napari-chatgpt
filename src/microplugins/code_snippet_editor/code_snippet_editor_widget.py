import os
import subprocess
import sys
from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics, QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QSplitter,
    QListWidget,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QShortcut,
    QToolBar,
    QStyle,
    QMenu,
    QAction,
)
from PyQt5.QtWidgets import QInputDialog, QMessageBox

from microplugins.code_snippet_editor.clickable_icon import ClickableIcon
from microplugins.code_snippet_editor.python_code_editor_widget import \
    PythonCodeEditor
from microplugins.code_snippet_editor.save_confirmation_widget import \
    SaveConfirmationWidget
from microplugins.formating.black_formating import format_code


class CodeSnippetEditorWidget(QWidget):
    def __init__(self, folder_path: str):
        """
        Create a widget for editing Python code snippets.

        Parameters
        ----------
        folder_path : str
            The path to the folder containing the Python code snippets.
        """
        super().__init__()
        self.folder_path = folder_path
        self.filename_to_displayname = {}
        self.displayname_to_filename = {}
        self.currently_open_filename = None
        self.init_UI()
        self.modified = False

    def init_UI(self):
        main_layout = QVBoxLayout(self)

        # Initialize the toolbar
        self.toolbar = QToolBar("Main Toolbar")
        main_layout.addWidget(self.toolbar)

        # New file button with a standard icon:
        icon = QApplication.style().standardIcon(QStyle.SP_FileIcon)
        new_file_clickable_icon = ClickableIcon(icon)
        self.toolbar.addWidget(new_file_clickable_icon)
        new_file_clickable_icon.clicked.connect(self.new_file)

        # Save file button with a custom icon:
        icon = QApplication.style().standardIcon(QStyle.SP_DialogSaveButton)
        save_file_clickable_icon = ClickableIcon(icon)
        self.toolbar.addWidget(save_file_clickable_icon)
        save_file_clickable_icon.clicked.connect(self.save_current_file)

        # Delete file button with a custom icon:
        icon = QApplication.style().standardIcon(QStyle.SP_TrashIcon)
        delete_file_clickable_icon = ClickableIcon(icon)
        self.toolbar.addWidget(delete_file_clickable_icon)
        delete_file_clickable_icon.clicked.connect(self.delete_current_file)

        # Improve code in file button with a custom icon:
        icon = QApplication.style().standardIcon(QStyle.SP_FileDialogContentsView)
        improve_file_clickable_icon = ClickableIcon(icon)
        self.toolbar.addWidget(improve_file_clickable_icon)
        improve_file_clickable_icon.clicked.connect(self.improve_current_file)

        # Run file button with a custom icon:
        icon = QApplication.style().standardIcon(QStyle.SP_MediaPlay)
        run_file_clickable_icon = ClickableIcon(icon)
        self.toolbar.addWidget(run_file_clickable_icon)
        run_file_clickable_icon.clicked.connect(self.run_current_file)

        # Splitter for the list widget and the code editor:
        self.splitter = QSplitter(Qt.Horizontal)

        # List widget for the file names:
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        # Code editor widget:
        self.code_editor = PythonCodeEditor()

        # Add widgets to the splitter:
        self.splitter.addWidget(self.list_widget)
        self.splitter.addWidget(self.code_editor)

        # Add the splitter to the main layout:
        main_layout.addWidget(self.splitter)

        # Save confirmation widget
        self.save_confirmation_widget = SaveConfirmationWidget()
        self.save_confirmation_widget.hide()  # Hide by default

        # Add the save confirmation widget to the main layout:
        main_layout.addWidget(self.save_confirmation_widget)

        # Set the layout for the main widget:
        self.setLayout(main_layout)

        # Connect signals and slots:
        self.list_widget.currentItemChanged.connect(self.current_list_item_changed)
        self.code_editor.textChanged.connect(self.on_text_modified)

        # Setting up the CTRL+S shortcut for saving the current file
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current_file)

        self.populate_list()

    def populate_list(self):
        self.list_widget.clear()
        self.filename_to_displayname.clear()
        self.displayname_to_filename.clear()
        maxWidth = 0
        fm = QFontMetrics(self.list_widget.font())
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".py"):
                display_name = self.truncate_filename(filename)
                self.filename_to_displayname[filename] = display_name
                self.displayname_to_filename[display_name] = filename
                self.list_widget.addItem(display_name)
                itemWidth = fm.width(display_name) + 10
                maxWidth = max(maxWidth, itemWidth)

        self.list_widget.setMaximumWidth(maxWidth)

    def truncate_filename(self, filename):
        max_length = 40
        if len(filename) > max_length:
            extension = filename.split(".")[-1]
            base_length = max_length - len(extension) - 3
            return f"{filename[:base_length]}(...).{extension}"
        return filename

    def on_text_modified(self):
        self.modified = True

    def load_snippet(self, show_confirmation=True):

        current = self.list_widget.currentItem()
        if current:
            display_name = current.text()
            filename = self.displayname_to_filename.get(display_name, "")

            # Check that the current file is not already open:
            if filename != self.currently_open_filename:
                # if the current file is modified and we are opening a new file, show a confirmation dialog:
                if show_confirmation and self.modified:

                    self.show_save_confirmation(lambda: self._load_snippet_no_checks(filename))
                    return  # Prevent loading a new file until decision is made

            self._load_snippet_no_checks(filename)

    def _load_snippet_no_checks(self, filename):
        self.currently_open_filename = filename
        with open(os.path.join(self.folder_path, filename), "r") as file:
            self.code_editor.setPlainText(file.read())
        self.modified = False  # Reset modified flag after loading file

    def show_save_confirmation(self, do_after_callable: Callable = None):
        # Update the message to include the filename that might be saved
        filename = (
            os.path.basename(self.currently_open_filename)
            if self.currently_open_filename
            else "the file"
        )
        self.save_confirmation_widget.setFilename(filename)
        self.save_confirmation_widget.setCallbacks(
            self.save_current_file, self.discard_changes, do_after_callable
        )
        self.save_confirmation_widget.show()

    def discard_changes(self):
        self.modified = False
        # Proceed to load the new file without saving:
        self.load_snippet()

    def save_current_file(self):
        if self.currently_open_filename:
            full_path = os.path.join(self.folder_path, self.currently_open_filename)
            with open(full_path, "w") as file:
                file.write(self.code_editor.toPlainText())
            self.modified = False

    def new_file(self):

        # Is current file modified?
        if self.modified:
            # Save current file:
            self.show_save_confirmation()

        # Ask for new file name:
        text, ok = QInputDialog.getText(self, "New File", "Enter file name:")

        # remove extension if provided, assuming that there could be multiple extensions (dots):
        text = text.split(".")[0]

        if ok and text:

            # Define filename and path:
            filename = f"{text}.py"
            full_path = os.path.join(self.folder_path, filename)

            # Check if file already exists:
            if os.path.exists(full_path):
                QMessageBox.warning(
                    self,
                    "File Exists",
                    "The file already exists. Please choose a different name.",
                )
                return

            # Create an empty Python file:
            with open(full_path, "w") as file:
                file.write("")

            # Repopulate the list:
            self.populate_list()

            # Select the newly created file:
            self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def duplicate_file(self):

        # get current item:
        current_item = self.list_widget.currentItem()

        if current_item:

            # Get original filename and display name:
            original_display_name = current_item.text()
            original_filename = self.displayname_to_filename[original_display_name]

            # get base name and extension:
            base_name, ext = os.path.splitext(original_filename)

            # New filename:
            new_filename = f"{base_name}_copy{ext}"
            #new_display_name = f"{base_name}_copy"

            # Ensure the new filename does not already exist
            counter = 1
            while os.path.exists(os.path.join(self.folder_path, new_filename)):
                counter += 1
                new_filename = f"{base_name}_copy{counter}{ext}"
                #new_display_name = f"{base_name}_copy{counter}"

            # Copy the file on disk
            with open(
                os.path.join(self.folder_path, original_filename), "r"
            ) as original_file:
                with open(
                    os.path.join(self.folder_path, new_filename), "w"
                ) as new_file:
                    new_file.write(original_file.read())

            # Update the list and dictionaries:
            self.populate_list()

    def delete_file_from_context_menu(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            filename_to_delete = self.displayname_to_filename[current_item.text()]
            self.delete_current_file(filename_to_delete)

    def delete_current_file(self, filename=None):
        # Determine which file to delete:
        file_to_delete = filename if filename else self.currently_open_filename

        if file_to_delete:
            # Ask for confirmation before deleting the file:
            reply = QMessageBox.question(
                self,
                "Delete File",
                "Are you sure you want to delete this file?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            # Check response:
            if reply == QMessageBox.Yes:
                # remove file:
                os.remove(os.path.join(self.folder_path, file_to_delete))
                self.populate_list()  # Refresh the list after deletion
                # Clear the editor and reset the current filename if it was the deleted file
                if file_to_delete == self.currently_open_filename:
                    # Select the file next to the one deleted, or clear the editor if there are no more files:

                    if self.list_widget.count() > 0:
                        self.list_widget.setCurrentRow(0)
                    else:
                        self.code_editor.clear()
                        self.currently_open_filename = None

    def rename_file(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            self.save_current_file()
            old_display_name = current_item.text()
            old_filename = self.displayname_to_filename[old_display_name]
            new_name, ok = QInputDialog.getText(
                self, "Rename file", "New name:", text=old_filename[:-3]
            )  # Exclude '.py' extension
            if ok and new_name:
                new_filename = f"{new_name}.py"
                # Rename file on disk
                os.rename(
                    os.path.join(self.folder_path, old_filename),
                    os.path.join(self.folder_path, new_filename),
                )
                # Update dictionaries
                del self.displayname_to_filename[old_display_name]
                self.filename_to_displayname[new_filename] = new_name
                self.displayname_to_filename[new_name] = new_filename
                # Update list widget item
                current_item.setText(new_name)
                # If this file is currently open, update the currently open filename
                if self.currently_open_filename == old_filename:
                    self.currently_open_filename = new_filename

    def improve_current_file(self):
        # This is a placeholder for your improvement logic, which could be code formatting, linting, etc.
        # For example, using a tool like black for code formatting:
        if self.currently_open_filename:
            code = self.code_editor.toPlainText()
            formatted_code = format_code(code)
            self.code_editor.setPlainText(formatted_code)
            self.modified = True

    def run_current_file(self):
        if self.currently_open_filename:

            # Save the file before running it:
            self.save_current_file()

            full_path = os.path.join(self.folder_path, self.currently_open_filename)
            subprocess.run(["python", full_path], capture_output=False)

    def show_context_menu(self, position):
        context_menu = QMenu(self)
        rename_action = QAction("Rename", self)
        duplicate_action = QAction("Duplicate", self)
        delete_action = QAction("Delete", self)

        context_menu.addAction(rename_action)
        context_menu.addAction(duplicate_action)
        context_menu.addAction(delete_action)

        rename_action.triggered.connect(self.rename_file)
        duplicate_action.triggered.connect(self.duplicate_file)
        delete_action.triggered.connect(self.delete_file_from_context_menu)

        context_menu.exec_(self.list_widget.mapToGlobal(position))

    def current_list_item_changed(self, current, previous):
        if current and (previous == None or current.text != previous.text()):
            self.load_snippet()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = QMainWindow()
    codeEditorWidget = CodeSnippetEditorWidget("")
    mainWindow.setCentralWidget(codeEditorWidget)
    mainWindow.setWindowTitle("Python Code Snippet Editor")
    mainWindow.resize(800, 600)
    mainWindow.show()

    sys.exit(app.exec_())
