import sys

from PyQt5.QtCore import QStringListModel, Qt
from PyQt5.QtWidgets import QApplication, QTextEdit, QCompleter, QVBoxLayout, QWidget
from jedi import Interpreter

class PythonCodeCompleter(QCompleter):
    def __init__(self, parent=None):
        super(PythonCodeCompleter, self).__init__(parent)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.interpreter = None

    def updateCompletions(self, text):
        if self.interpreter is None:
            self.interpreter = Interpreter(text, [])
        else:
            self.interpreter = Interpreter(text, self.interpreter.namespaces)
        completions = [c.name for c in self.interpreter.complete()]
        self.setModel(QStringListModel(completions))
