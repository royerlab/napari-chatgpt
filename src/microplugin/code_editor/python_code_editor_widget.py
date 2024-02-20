import jedi  # Make sure jedi is installed
from qtpy.QtCore import QStringListModel
from qtpy.QtCore import Qt
from qtpy.QtGui import QTextCursor
from qtpy.QtWidgets import (
    QPlainTextEdit,
    QCompleter,
)

from microplugin.code_editor.python_syntax_highlighting import \
    PythonSyntaxHighlighter


class PythonCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Tab Length Customization
        self.tab_length = 4  # Default to 4 spaces
        self.setTabStopDistance(self.fontMetrics().width(" ") * self.tab_length)

        # Set placeholder text:
        self.setPlaceholderText("Type your code here...")

        # Syntax highlighter:
        self.python_syntax_highlighter = PythonSyntaxHighlighter(
            self.document())

        # Completer setup:
        self.completer = QCompleter(self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insertCompletion)

    def textUnderCursor(self):
        text_cursor = self.textCursor()
        text_cursor.select(QTextCursor.WordUnderCursor)
        return text_cursor.selectedText()

    def insertCompletion(self, completion):
        if self.completer.widget() != self:
            return
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])  # insert the selected completion
        self.setTextCursor(tc)

    def keyPressEvent(self, event):
        if self.completer:
            if self.completer.popup().isVisible():
                if event.key() in (
                        Qt.Key_Enter,
                        Qt.Key_Return,
                        Qt.Key_Escape,
                        Qt.Key_Tab,
                        Qt.Key_Backtab,
                ):
                    # Ignore the event if the completer is visible and the key is one of the above:
                    event.ignore()
                    return
                # Hide the completer when the user types a character:
                self.completer.popup().hide()

        if event.text() == ".":
            # Show completions after typing a dot:
            super().keyPressEvent(event)
            self.updateCompleter(show_completions=True)
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Indent new lines after certain keywords:
            cursor = self.textCursor()
            line = cursor.block().text()
            indentation = len(line) - len(line.lstrip(" "))
            should_indent = any(
                kw in line
                for kw in [
                    "if",
                    "elif",
                    "else",
                    "for",
                    "while",
                    "try",
                    "except",
                    "finally",
                    "with",
                    "def",
                    "class",
                ]
            ) or line.endswith(":")

            # Insert new line and indentation:
            super().keyPressEvent(event)
            self.insertPlainText(
                " " * (indentation + (self.tab_length if should_indent else 0))
            )
        else:
            super().keyPressEvent(event)
            self.updateCompleter()

    def updateCompleter(self, show_completions=False):
        text_under_cursor = self.textUnderCursor()
        if text_under_cursor != "" or show_completions:

            # Get completions from Jedi:
            script = jedi.Script(code=self.toPlainText(), path="temp.py")
            completions = script.complete(
                line=self.textCursor().blockNumber() + 1,
                column=self.textCursor().columnNumber(),
            )
            completion_list = [c.name for c in completions]

            # Update the completer model and show it:
            self.completer.setModel(QStringListModel(completion_list))
            if completion_list:
                self.completer.setCompletionPrefix(text_under_cursor)
                cr = self.cursorRect()
                cr.setWidth(
                    self.completer.popup().sizeHintForColumn(0)
                    + self.completer.popup().verticalScrollBar().sizeHint().width()
                )
                self.completer.complete(cr)  # popup it up!
        elif show_completions:
            # Close the completer if there's no text under cursor and no force show
            self.completer.popup().hide()

    def setPlainTextUndoable(self, text):
        # Obtain the current text cursor from the editor
        tc = self.textCursor()

        # Start an undoable operation
        tc.beginEditBlock()

        # Select all text
        tc.select(QTextCursor.Document)

        # Remove the selected text (the entire document content)
        tc.removeSelectedText()

        # Insert the new text
        tc.insertText(text)

        # End the undoable operation
        tc.endEditBlock()