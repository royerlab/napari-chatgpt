from jedi import Interpreter
from qtpy.QtCore import QStringListModel, Qt
from qtpy.QtWidgets import QCompleter


class PythonCodeCompleter(QCompleter):
    def __init__(self, parent=None):
        super(PythonCodeCompleter, self).__init__(parent)

        # Set the completion mode to PopupCompletion to display the completions in a popup:
        self.setCompletionMode(QCompleter.PopupCompletion)

        # Set the case sensitivity to case insensitive:
        self.setCaseSensitivity(Qt.CaseInsensitive)

        # Set the model to an empty QStringListModel:
        self.interpreter = None

    def updateCompletions(self, text):
        if self.interpreter is None:
            self.interpreter = Interpreter(text, [])
        else:
            self.interpreter = Interpreter(text, self.interpreter.namespaces)
        completions = [c.name for c in self.interpreter.complete()]
        self.setModel(QStringListModel(completions))
