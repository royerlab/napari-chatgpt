"""Widget for managing and editing a folder of Python code snippets.

Provides a file list, multi-tab code editor, toolbar with actions (new, duplicate,
delete, format, AI-assisted operations), network code sharing via CodeDrop,
and an integrated console for script execution output.
"""

import json
import os
import sys
from datetime import datetime

import qtawesome
from arbol import aprint
from qtpy.QtCore import Qt
from qtpy.QtGui import QFontMetrics
from qtpy.QtWidgets import (
    QAction,
    QApplication,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QSizePolicy,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.microplugin.code_editor.clickable_icon import ClickableIcon
from napari_chatgpt.microplugin.code_editor.code_drop_send_widget import (
    CodeDropSendWidget,
)
from napari_chatgpt.microplugin.code_editor.console_widget import ConsoleWidget
from napari_chatgpt.microplugin.code_editor.python_code_editor_manager import (
    MultiEditorManager,
)
from napari_chatgpt.microplugin.code_editor.text_dialog import TextDialog
from napari_chatgpt.microplugin.code_editor.text_input_widget import TextInputWidget
from napari_chatgpt.microplugin.code_editor.yes_no_cancel_question_widget import (
    YesNoCancelQuestionWidget,
)
from napari_chatgpt.microplugin.formating.black_formating import format_code
from napari_chatgpt.microplugin.network.code_drop_client import CodeDropClient
from napari_chatgpt.microplugin.network.code_drop_server import CodeDropServer


class CodeSnippetEditorWidget(QWidget):
    """Main widget for browsing, editing, and running Python code snippets.

    Combines a file list sidebar, a multi-file code editor with syntax
    highlighting and auto-completion, a toolbar with file management and
    AI-powered actions, network code sharing (CodeDrop), and an output
    console.

    Attributes:
        folder_path: Path to the directory containing ``.py`` snippet files.
        variables: Variables injected into the execution namespace when running code.
        client: CodeDrop network client for peer discovery and sending.
        server: CodeDrop network server for receiving code from peers.
        is_llm_available: Whether an LLM API is available for AI features.
        llm_model_name: Model name used for AI-powered code operations.
    """

    def __init__(self, folder_path: str, variables: dict | None = None, parent=None):
        """Initialize the code snippet editor widget.

        Args:
            folder_path: Path to the folder containing Python code snippets.
            variables: Optional dict of variables available when executing snippets.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.folder_path = folder_path
        self.filename_to_displayname = {}
        self.displayname_to_filename = {}
        self.currently_open_filename = None

        # Dictionary to hold undo stacks for each file
        self.undo_stacks = {}

        # Set the variables:
        self.variables = variables or {}

        # Start the network client and server:
        self.client = CodeDropClient()
        self.client.discover_worker.server_discovered.connect(self.on_server_discovered)
        self.client.start_discovering()

        # Start the server:
        self.server = CodeDropServer(self.server_message_received)
        self.server.start_broadcasting()
        self.server.start_receiving()

        # Check if LLMs are available:
        self.is_llm_available = is_llm_available()

        # Initialize the UI:
        self.init_UI()

        # Set the default model name for the language model:
        self.llm_model_name = None

    def init_UI(self):
        """Build the complete UI: toolbar, file list, editor, and auxiliary widgets."""
        main_layout = QVBoxLayout(self)

        # Initialize the toolbar
        self.toolbar = QToolBar("Main Toolbar")
        main_layout.addWidget(self.toolbar)

        # Icon color:
        icon_color = "#5E636F"

        # function to get icon from fontawesome:
        def _get_icon(icon_name: str):
            return qtawesome.icon(icon_name, color=icon_color)

        # New file button with a standard icon:
        new_file_clickable_icon = ClickableIcon(_get_icon("fa5s.file-alt"))
        new_file_clickable_icon.setToolTip("New file")
        self.toolbar.addWidget(new_file_clickable_icon)
        new_file_clickable_icon.clicked.connect(self.new_file_dialog)

        # Duplicate file button with a custom icon:
        duplicate_file_clickable_icon = ClickableIcon(_get_icon("fa5s.copy"))
        duplicate_file_clickable_icon.setToolTip("Duplicate file")
        self.toolbar.addWidget(duplicate_file_clickable_icon)
        duplicate_file_clickable_icon.clicked.connect(self.duplicate_file)

        # Delete file button with a custom icon:
        delete_file_clickable_icon = ClickableIcon(_get_icon("fa5s.trash-alt"))
        delete_file_clickable_icon.setToolTip("Delete file")
        self.toolbar.addWidget(delete_file_clickable_icon)
        delete_file_clickable_icon.clicked.connect(self.delete_file)

        # Clean and reformat code in file button with a custom icon:
        clean_file_clickable_icon = ClickableIcon(_get_icon("fa5s.hand-sparkles"))
        clean_file_clickable_icon.setToolTip("Clean and reformat code")
        self.toolbar.addWidget(clean_file_clickable_icon)
        clean_file_clickable_icon.clicked.connect(self.clean_and_reformat_current_file)

        # Check if the OpenAI API key is available:
        if self.is_llm_available:
            # Check if the file is 'safe':
            check_code_safety_clickable_icon = ClickableIcon(
                _get_icon("fa5s.virus-slash")
            )
            check_code_safety_clickable_icon.setToolTip("Check code safety")
            self.toolbar.addWidget(check_code_safety_clickable_icon)
            check_code_safety_clickable_icon.clicked.connect(
                self.check_code_safety_with_AI
            )

            # Improve code in file button with a custom icon:
            comment_code_clickable_icon = ClickableIcon(_get_icon("fa5s.edit"))
            comment_code_clickable_icon.setToolTip(
                "Improve code comments and explanations"
            )
            self.toolbar.addWidget(comment_code_clickable_icon)
            comment_code_clickable_icon.clicked.connect(self.comment_code_with_AI)

            # Use AI to change code based on prompt:
            modify_code_clickable_icon = ClickableIcon(_get_icon("fa5s.robot"))
            modify_code_clickable_icon.setToolTip("Modify code with AI")
            self.toolbar.addWidget(modify_code_clickable_icon)
            modify_code_clickable_icon.clicked.connect(self.modify_code_with_AI)

        # Send file button with a custom icon:
        send_file_clickable_icon = ClickableIcon(_get_icon("fa5s.wifi"))
        send_file_clickable_icon.setToolTip("Send file")
        self.toolbar.addWidget(send_file_clickable_icon)
        send_file_clickable_icon.clicked.connect(self.send_current_file)

        # Create a spacer widget and set its size policy to expanding
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)

        # Run file button with a custom icon:
        run_file_clickable_icon = ClickableIcon(_get_icon("fa5s.play-circle"))
        run_file_clickable_icon.setToolTip("Run file")
        self.toolbar.addWidget(run_file_clickable_icon)
        run_file_clickable_icon.clicked.connect(self.run_current_file)

        # Splitter for the list widget and the code editor:
        self.splitter = QSplitter(Qt.Horizontal)

        # List widget for the file names:
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        # Code editor widget:
        self.editor_manager = MultiEditorManager(self.on_text_modified)

        # Add widgets to the splitter:
        self.splitter.addWidget(self.list_widget)
        self.splitter.addWidget(self.editor_manager)

        # Add the splitter to the main layout:
        main_layout.addWidget(self.splitter)

        # Add YesNoCancelQuestionWidget to the main layout:
        self.yes_no_cancel_question_widget = YesNoCancelQuestionWidget()
        main_layout.addWidget(self.yes_no_cancel_question_widget)

        # Add TextInputQuestionWidget to the main layout:
        self.text_input_widget = TextInputWidget()
        main_layout.addWidget(self.text_input_widget)

        # Add CodeDropSendWidget to the main layout:
        self.code_drop_send_widget = CodeDropSendWidget(self.client)
        main_layout.addWidget(self.code_drop_send_widget)

        # Add ConsoleWidget to the main layout:
        self.console_widget = ConsoleWidget()
        main_layout.addWidget(self.console_widget)

        # Set the layout for the main widget:
        self.setLayout(main_layout)

        # Connect signals and slots:
        self.list_widget.currentItemChanged.connect(self.current_list_item_changed)

        self.populate_list()

    def show_context_menu(self, position):
        """Display a right-click context menu for the file list.

        Args:
            position: The local position where the context menu was requested.
        """

        # Create the context menu:
        context_menu = QMenu(self)

        # Instantiate actions for the context menu:
        refresh_action = QAction("Refresh file list", self)
        rename_action = QAction("Rename", self)
        duplicate_action = QAction("Duplicate", self)
        delete_action = QAction("Delete", self)
        open_in_system = QAction("Open in system", self)
        find_in_system = QAction("Find in system", self)

        # Instantiate AI actions for the context menu:
        if self.is_llm_available:
            clean_action = QAction("Clean", self)
            check_action = QAction("Check", self)
            comment_action = QAction("Comment", self)
            modify_action = QAction("Modify", self)

        # Add actions to the context menu:
        context_menu.addAction(refresh_action)
        context_menu.addAction(rename_action)
        context_menu.addAction(duplicate_action)
        context_menu.addAction(delete_action)
        context_menu.addAction(open_in_system)
        context_menu.addAction(find_in_system)

        # Add AI actions to the context menu:
        if self.is_llm_available:
            context_menu.addAction(clean_action)
            context_menu.addAction(check_action)
            context_menu.addAction(comment_action)
            context_menu.addAction(modify_action)

        # Connect the actions to the corresponding slots:
        refresh_action.triggered.connect(self.populate_list)
        rename_action.triggered.connect(self.rename_file)
        duplicate_action.triggered.connect(self.duplicate_file)
        delete_action.triggered.connect(self.delete_file_from_context_menu)
        open_in_system.triggered.connect(self.open_file_in_system)
        find_in_system.triggered.connect(self.find_file_in_system)

        # Connect AI actions to the corresponding slots:
        if self.is_llm_available:
            clean_action.triggered.connect(self.clean_and_reformat_current_file)
            check_action.triggered.connect(self.check_code_safety_with_AI)
            comment_action.triggered.connect(self.comment_code_with_AI)
            modify_action.triggered.connect(self.modify_code_with_AI)

        # Show the context menu:
        context_menu.exec_(self.list_widget.mapToGlobal(position))

    def on_server_discovered(self, server_name, server_address, port_number):
        """Log a newly discovered CodeDrop server."""
        aprint(f"Discovered server: {server_name} at {server_address}:{port_number}")

    def server_message_received(self, addr, message):
        """Handle an incoming code message from a CodeDrop peer.

        Parses the JSON message, prepends provenance metadata, and prompts
        the user to accept or reject the received file.

        Args:
            addr: Tuple of ``(ip_address, port)`` of the sender.
            message: JSON-encoded string containing hostname, username,
                filename, and code fields.
        """

        # Get IP address and port number:
        ip_address, port = addr

        aprint(f"Message of length: {len(message)} received from {ip_address}:{port}")

        # Parse the message in JSON format:
        message_dict = json.loads(message)
        hostname = message_dict["hostname"]
        username = message_dict["username"]
        filename = message_dict["filename"]
        code = message_dict["code"]

        # Prepend a comment line to the code that gives the date and time it was received and from where
        code = (
            f"# File '{filename}' of length: {len(code)} received from {username} at {hostname} ({ip_address}:{port})  at {datetime.now()}\n"
            + code
        )

        # Ask for confirmation:
        message = f"Accept file '{filename}' sent by {username} at {hostname} ({ip_address}:{port})?"

        def _accept_file():
            self.new_file(filename=filename, code=code, postfix_if_exists="received")

        # Show the question widget:
        self.yes_no_cancel_question_widget.show_question(
            message=message, yes_callback=_accept_file, cancel_text=None
        )

    def populate_list(self, selected_filename: str | None = None):
        """Scan the folder and populate the file list widget with ``.py`` files.

        Args:
            selected_filename: If provided, select and load this file after
                populating. Otherwise, selects the first file.
        """

        # Clear the list widget and dictionaries:
        self.list_widget.clear()
        self.filename_to_displayname.clear()
        self.displayname_to_filename.clear()
        self.currently_open_filename = None

        # Get the list of files in the folder:
        file_list = os.listdir(self.folder_path)

        # Sort the list of files:
        file_list.sort()

        # Reset the index for duplicated display names:
        display_name_index = 0

        # Populate the list widget with the Python files in the folder:
        max_width = 0
        fm = QFontMetrics(self.list_widget.font())
        for filename in file_list:
            if filename.endswith(".py"):
                # Add the file to the list widget:
                display_name = self.truncate_filename(filename)

                # If there is already a file with the same display name, add a number to the display name:
                if display_name in self.displayname_to_filename:
                    display_name_index += 1
                    display_name = self.truncate_filename(filename, display_name_index)
                else:
                    display_name_index = 0

                # Add the file to the dictionaries:
                self.filename_to_displayname[filename] = display_name
                self.displayname_to_filename[display_name] = filename

                # Create a QListWidgetItem for the file:
                item = QListWidgetItem(display_name)
                # Set the tooltip to the full filename if it has been truncated:
                if display_name != filename:
                    item.setToolTip(filename)

                # Add the item to the list widget:
                self.list_widget.addItem(item)

                # Update the maximum width:
                item_width = fm.width(display_name) + 20
                max_width = max(max_width, item_width)

        # Ensure that the list widget is wide enough to show the longest file name:
        self.list_widget.setMaximumWidth(max_width)

        # Ensure that the list widget cannot be too small
        self.list_widget.setMinimumWidth(fm.width("some_file.py") + 20)

        # Ensure that the selected file is loaded:
        if selected_filename:
            # Make sure to select the right row:
            for i in range(self.list_widget.count()):
                if self.list_widget.item(i).text() == self.filename_to_displayname.get(
                    selected_filename, ""
                ):
                    self.list_widget.setCurrentRow(i)
            self.load_snippet_by_filename(selected_filename)
        else:
            # Otherwise select the first file in the list if there is one using load_snippet_by_filename:
            if self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)
                self.load_snippet()

    def truncate_filename(
        self, filename: str, index: int | None = None, max_length: int = 40
    ) -> str:
        """Truncate a filename to fit within a maximum display length.

        Args:
            filename: The original filename to truncate.
            index: Optional numeric suffix to disambiguate duplicate display names.
            max_length: Maximum character length for the display name.

        Returns:
            The truncated filename with ellipsis, or the original if short enough.
        """

        # Convert index to string if it is not None:
        if index is not None:
            index_str = str(index)
        else:
            index_str = ""

        # Truncate the filename if it is too long:
        if len(filename) > max_length:
            extension = filename.split(".")[-1]
            base_length = max_length - len(extension) - 3
            return f"{filename[:base_length]}…{index_str}.{extension}"
        return filename

    def on_text_modified(self):
        """Auto-save callback triggered when the editor text changes."""
        # Save the file when the text is modified:
        self.save_current_file()

    def load_snippet(self):
        """Load the code snippet for the currently selected file list item."""

        # Get the current item:
        current = self.list_widget.currentItem()

        # If there is a current item:
        if current:
            # Get the filename from the display name:
            display_name = current.text()
            filename = self.displayname_to_filename.get(display_name, "")

            # Load the snippet by filename:
            self.load_snippet_by_filename(filename)

    def load_snippet_by_filename(self, filename):
        """Switch the editor to the given file and load its contents.

        Args:
            filename: Name of the ``.py`` file (relative to ``folder_path``).
        """

        # Switch editor to the file:
        self.editor_manager.switch_to(filename)

        # Set the currently open filename:
        self.currently_open_filename = filename

        # Load the snippet from the file:
        with open(os.path.join(self.folder_path, filename)) as file:
            self.editor_manager.current_editor.setPlainTextUndoable(file.read())

    def save_current_file(self):
        """Save the current editor contents to disk."""

        # If there is a currently open file, save it:
        if self.currently_open_filename:

            # Make sure that there is an editor <=> at least one file in the list:
            if not self.editor_manager.current_editor:
                return

            # Get the full path to the file:
            full_path = os.path.join(self.folder_path, self.currently_open_filename)

            # Save the file:
            with open(full_path, "w") as file:
                file.write(self.editor_manager.current_editor.toPlainText())

    def new_file(self, filename: str, code: str | None = "", postfix_if_exists="_copy"):
        """Create a new Python file in the folder and refresh the list.

        If a file with the given name already exists, a postfix is appended
        (with an incrementing number) to avoid overwriting.

        Args:
            filename: Desired filename (``'.py'`` extension added if missing).
            code: Initial code content for the new file.
            postfix_if_exists: Suffix appended to avoid name collisions.
        """

        # Make sure the file has '.py' extension:
        if not filename.endswith(".py"):
            filename = f"{filename}.py"

        # Full path to the file:
        full_path = os.path.join(self.folder_path, filename)

        # Make sure the file does not already exist:
        while os.path.exists(full_path):
            # Get filename from fullpath:
            _, filename = os.path.split(full_path)

            # Get the filename without extension:
            base_name, ext = os.path.splitext(filename)

            # If the filename already contains the postfix, the we check if there is number after the postfix:
            if postfix_if_exists in base_name:
                # Get the number after the postfix:
                postfix_number = base_name.split(postfix_if_exists)[-1]
                try:
                    postfix_number = int(postfix_number)
                except ValueError:
                    postfix_number = 0

                # Increase the number and add it to the base name:
                base_name = base_name.split(postfix_if_exists)[0]
                base_name = f"{base_name}{postfix_if_exists}{postfix_number + 1}"

                # Change the filename to avoid overwriting the existing file:
                filename = f"{base_name}{ext}"
            else:
                # Add the postfix to the base name:
                base_name = f"{base_name}{postfix_if_exists}"
                # Change the filename to avoid overwriting the existing file:
                filename = f"{base_name}{ext}"

            # Update the full path:
            full_path = os.path.join(self.folder_path, filename)

        # Create the file and write the text to it:
        with open(full_path, "w") as file:
            file.write(code)

        # Repopulate the list:
        self.populate_list(filename)

    def new_file_dialog(self):
        """Show a text input dialog prompting the user for a new filename."""

        def _new_file(filename_text: str):
            # if no file is selected but the editor has contents, use it as the new file's content:

            if self.editor_manager.current_editor:
                current_editor = self.editor_manager.current_editor
                current_text_in_editor = current_editor.toPlainText()
                if (
                    self.currently_open_filename is None
                    and current_text_in_editor
                    and len(current_text_in_editor) > 0
                ):
                    code = current_editor.toPlainText()
                else:
                    code = ""
            else:
                code = ""

            self.new_file(filename=filename_text, code=code)

        # Show the text input widget:
        self.text_input_widget.show_input(
            message="Enter file name:",
            enter_text="Create",
            cancel_text="Cancel",
            enter_callback=_new_file,
            cancel_callback=None,
            do_after_callable=None,
        )

    def duplicate_file(self):
        """Duplicate the currently selected file with a ``_copy`` suffix."""

        # get current item:
        current_item = self.list_widget.currentItem()

        if current_item:

            # Save current file:
            self.save_current_file()

            # Get original filename and display name:
            original_display_name = current_item.text()
            original_filename = self.displayname_to_filename[original_display_name]

            # get base name and extension:
            base_name, ext = os.path.splitext(original_filename)

            # New filename:
            new_filename = f"{base_name}_copy{ext}"
            # new_display_name = f"{base_name}_copy"

            # Ensure the new filename does not already exist
            counter = 1
            while os.path.exists(os.path.join(self.folder_path, new_filename)):
                counter += 1
                new_filename = f"{base_name}_copy{counter}{ext}"
                # new_display_name = f"{base_name}_copy{counter}"

            # Copy the file on disk
            with open(
                os.path.join(self.folder_path, original_filename)
            ) as original_file:
                with open(
                    os.path.join(self.folder_path, new_filename), "w"
                ) as new_file:
                    new_file.write(original_file.read())

            # Update the list and dictionaries:
            self.populate_list(new_filename)

    def delete_file_from_context_menu(self):
        """Delete the file selected via the context menu."""

        # Get current item:
        current_item = self.list_widget.currentItem()

        # If there is a current item:
        if current_item:
            # Get the filename from the display name:
            filename_to_delete = self.displayname_to_filename[current_item.text()]

            # Delete the file:
            self.delete_file(filename_to_delete)

    def delete_file(self, filename=None):
        """Prompt for confirmation and delete the specified or current file.

        Args:
            filename: File to delete. Defaults to the currently open file.
        """
        # Determine which file to delete:
        file_to_delete = filename or self.currently_open_filename

        # If there is a file to delete:
        if file_to_delete:

            # Ask for confirmation:
            message = f"Are you sure you want to delete file {file_to_delete}?"

            def _delete_file():
                # Get the full path to the file:
                file_to_delete_path = os.path.join(self.folder_path, file_to_delete)

                # remove file:
                os.remove(file_to_delete_path)

                # Refresh the list after deletion:
                self.populate_list()

                if self.list_widget.count() > 0:
                    self.list_widget.setCurrentRow(0)
                    self.load_snippet()
                else:
                    self.editor_manager.current_editor.clear()
                    self.currently_open_filename = None

            # Show the question widget:
            self.yes_no_cancel_question_widget.show_question(
                message=message, yes_callback=_delete_file, cancel_text=None
            )

    def rename_file(self):
        """Show a text input dialog to rename the currently selected file."""

        # Get current line:
        current_item = self.list_widget.currentItem()

        if current_item:
            # Save current file:
            self.save_current_file()

            # Get original filename and display name:
            old_display_name = current_item.text()
            old_filename = self.displayname_to_filename[old_display_name]

            def _rename_file(new_name: str):
                # New filename:
                new_filename = f"{new_name}.py"

                # Rename file on disk
                os.rename(
                    os.path.join(self.folder_path, old_filename),
                    os.path.join(self.folder_path, new_filename),
                )

                # Update the list and dictionaries:
                self.populate_list(new_filename)

            self.text_input_widget.show_input(
                message="Enter new file name:",
                placeholder_text="Enter new name here",
                default_text=old_filename[:-3],
                enter_text="Rename",
                cancel_text="Cancel",
                enter_callback=_rename_file,
                cancel_callback=None,
                do_after_callable=None,
            )

            # # Ask for new name:
            # new_name, ok = QInputDialog.getText(
            #     self, "Rename file", "New name:", text=old_filename[:-3]
            # )  # Exclude '.py' extension

    def clean_and_reformat_current_file(self):
        """Reformat the current file's code using Black and save it."""
        if self.currently_open_filename:

            # Make sure that there is an editor <=> at least one file in the list:
            if not self.editor_manager.current_editor:
                return

            # Get the code from the editor:
            code = self.editor_manager.current_editor.toPlainText()

            # Uses black to format the code:
            formatted_code = format_code(code)

            # Set the formatted code in the editor:
            self.editor_manager.current_editor.setPlainTextUndoable(formatted_code)

            # Save the file after improving it:
            self.save_current_file()

    def open_file_in_system(self):
        """Open the currently selected file with the system's default application."""
        # Get current item:
        current_item = self.list_widget.currentItem()

        if current_item:
            # Get the filename from the display name:
            filename_to_open = self.displayname_to_filename[current_item.text()]

            # Open the file in the system for different OS:
            # First OSX:
            if sys.platform == "darwin":
                os.system(f"open {os.path.join(self.folder_path, filename_to_open)}")
            # Then Windows:
            elif (
                sys.platform == "win32"
                or sys.platform == "cygwin"
                or sys.platform == "msys"
                or sys.platform == "win64"
            ):
                os.system(f"start {os.path.join(self.folder_path, filename_to_open)}")
            # Then Linux:
            else:
                os.system(
                    f"xdg-open {os.path.join(self.folder_path, filename_to_open)}"
                )

    def find_file_in_system(self):
        """Open the snippet folder in the system's file manager."""

        # Open the folder in the system for different OS:
        # First OSX:
        if sys.platform == "darwin":
            os.system(f"open {self.folder_path}")
        # Then Windows:
        elif (
            sys.platform == "win32"
            or sys.platform == "cygwin"
            or sys.platform == "msys"
            or sys.platform == "win64"
        ):
            os.system(f"start {self.folder_path}")
        # Then Linux:
        else:
            os.system(f"xdg-open {self.folder_path}")

    def check_code_safety_with_AI(self):
        """Use an LLM to analyze the current file's code for safety concerns."""
        if self.currently_open_filename:

            # Make sure that there is an editor <=> at least one file in the list:
            if not self.editor_manager.current_editor:
                return

            # Get the code from the editor:
            code = self.editor_manager.current_editor.toPlainText()

            # Check the code for safety by calling ChatGPT with a custom prompt:
            from napari_chatgpt.utils.python.check_code_safety import check_code_safety

            response, safety_rank = check_code_safety(
                code, model_name=self.llm_model_name, verbose=True
            )

            # Create the icons for the dialog:
            InformationIcon = qtawesome.icon("fa5s.info-circle")
            WarningIcon = qtawesome.icon("fa5s.exclamation-triangle")

            # Create and show the custom dialog
            dialog = TextDialog(
                f"Code Safety Report for: {self.currently_open_filename}",
                response,
                InformationIcon if safety_rank in ["A", "B"] else WarningIcon,
            )

            # Show the dialog:
            dialog.exec_()

    def comment_code_with_AI(self):
        """Use an LLM to add or improve comments and explanations in the current file."""
        if self.currently_open_filename:

            # Make sure that there is an editor <=> at least one file in the list:
            if not self.editor_manager.current_editor:
                return

            # Get the code from the editor:
            code = self.editor_manager.current_editor.toPlainText()

            # Add comments to the code:
            from napari_chatgpt.utils.python.add_comments import add_comments

            code = add_comments(code, model_name=self.llm_model_name, verbose=True)

            # Set the commented code in the editor:
            self.editor_manager.current_editor.setPlainTextUndoable(code)

    def modify_code_with_AI(self):
        """Prompt the user for instructions and use an LLM to modify the current code."""
        if self.currently_open_filename:

            def _modify_code(request: str):

                # If there is no currently open file, return:
                if not self.currently_open_filename:
                    return

                # Get the code from the editor:
                code = self.editor_manager.current_editor.toPlainText()

                # Modify the code based on the request:
                from napari_chatgpt.utils.python.modify_code import modify_code

                modified_code = modify_code(
                    code=code,
                    request=request,
                    model_name=self.llm_model_name,
                    verbose=True,
                )

                # Request without new line characters:
                request_nonl = request.replace("\n", " ")

                # Add comment to the code that explains what as changed:
                modified_code = f"# Code modified by Omega at {datetime.now()}.\n# Request:{request_nonl}.\n\n{modified_code}"

                # Set the commented code in the editor:
                self.editor_manager.current_editor.setPlainTextUndoable(modified_code)

            placeholder_text = (
                "Explain how you you want to modify the code of the currently selected file.\n"
                "For example:\n"
                "   'Make a widget from this code',\n"
                "   'Make the code work for 3d stacks',\n"
                "   etc...\n"
                "You can also place 'TODO's or 'FIXME' in the code, in that case no prompt is required.\n"
                "Finally, you can undo the changes with CTRL+Z.\n"
            )

            # Show the text input widget:
            self.text_input_widget.show_input(
                message="Prompt:",
                placeholder_text=placeholder_text,
                enter_text="Modify",
                cancel_text="Cancel",
                enter_callback=_modify_code,
                cancel_callback=None,
                do_after_callable=None,
                multi_line=True,
                max_height=200,
            )

    def send_current_file(self):
        """Open the CodeDrop send dialog for the currently open file."""

        # Send the file if there is a currently open file:
        if self.currently_open_filename:

            def _get_current_code_and_filename():
                # Get the code from the editor:
                if self.editor_manager.current_editor:
                    code = self.editor_manager.current_editor.toPlainText()
                    return self.currently_open_filename, code
                return None, None

            # Show the send dialog:
            self.code_drop_send_widget.show_send_dialog(
                get_code_callable=_get_current_code_and_filename
            )

    def run_current_file(self):
        """Execute the current file as a module and display output in the console."""

        # Run the file if there is a currently open file:
        if self.currently_open_filename:

            # Save the file before running it:
            self.save_current_file()

            # Make sure that there is an editor <=> at least one file in the list:
            if not self.editor_manager.current_editor:
                return

            # Get code from the editor:
            code = self.editor_manager.current_editor.toPlainText()

            try:
                # Local import to avoid circular import:
                from napari_chatgpt.utils.python.dynamic_import import execute_as_module

                # Run the code as a module:
                captured_output = execute_as_module(code, **self.variables)

                # Show the output in the console:
                self.console_widget.append_message(captured_output)

                aprint(f"Tool completed task successfully:\n {captured_output}")

            except Exception as e:
                aprint(f"Error running file: {e}")
                import traceback

                traceback.print_exc()

                # String that contains stacktrace:
                captured_stacktrace = traceback.format_exc()

                # Show the output in the console:
                self.console_widget.append_message(
                    captured_stacktrace, message_type="error"
                )

    def current_list_item_changed(self, current, previous):
        """Handle file list selection changes by loading the newly selected snippet."""

        # If the current item is different from the previous one, load the snippet:
        if current and (previous is None or current.text() != previous.text()):
            # Load the snippet:
            self.load_snippet()

    def close(self):
        """Stop network services, close editors, and clean up child widgets."""
        # Stop the server:
        self.server.stop()

        # Stop the client:
        self.client.stop()

        # Close the manager:
        self.editor_manager.close()

        # Close the widgets:
        self.yes_no_cancel_question_widget.close()
        self.text_input_widget.close()
        self.code_drop_send_widget.close()

        # Close the widget itself.
        super().close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = QMainWindow()
    codeEditorWidget = CodeSnippetEditorWidget("")
    mainWindow.setCentralWidget(codeEditorWidget)
    mainWindow.setWindowTitle("Python Code Snippet Editor")
    mainWindow.resize(800, 600)
    mainWindow.show()

    sys.exit(app.exec_())
