"""Jedi-based Python code completer for QPlainTextEdit widgets."""

from jedi import Interpreter
from qtpy.QtCore import QStringListModel, Qt
from qtpy.QtWidgets import QCompleter


class PythonCodeCompleter(QCompleter):
    """QCompleter that uses Jedi's Interpreter for Python code completions.

    Maintains a Jedi Interpreter across calls to preserve namespace context.
    Completions are case-insensitive and displayed in a popup.
    """

    def __init__(self, parent=None):
        """Initialize the completer with popup mode and case-insensitive matching."""
        super().__init__(parent)

        # Set the completion mode to PopupCompletion to display the completions in a popup:
        self.setCompletionMode(QCompleter.PopupCompletion)

        # Set the case sensitivity to case insensitive:
        self.setCaseSensitivity(Qt.CaseInsensitive)

        # Set the model to an empty QStringListModel:
        self.interpreter = None

    def updateCompletions(self, text):
        """Recompute completions for the given source text using Jedi.

        Args:
            text: The full Python source code to analyze for completions.
        """
        if self.interpreter is None:
            self.interpreter = Interpreter(text, [])
        else:
            self.interpreter = Interpreter(text, self.interpreter.namespaces)
        completions = [c.name for c in self.interpreter.complete()]
        self.setModel(QStringListModel(completions))
