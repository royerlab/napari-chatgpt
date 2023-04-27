import getpass
import getpass
import os
import socket
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal, QRegExp, QProcess, QThread
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, \
    QTextCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QPlainTextEdit, \
    QDesktopWidget


class PlainTextEdit(QPlainTextEdit):
    commandSignal = pyqtSignal(str)
    commandZPressed = pyqtSignal(str)

    def __init__(self, parent=None, movable=False):
        super().__init__(parent)

        self.name = "[" + str(getpass.getuser()) + "@" + str(
            socket.gethostname()) + "]" + "  ~" + str(
            os.getcwd()) + " >$ "
        self.appendPlainText(self.name)
        self.movable = movable
        self.parent = parent
        self.commands = []  # This is a list to track what commands the user has used so we could display them when
        # up arrow key is pressed
        self.tracker = 0
        self.setStyleSheet(
            "QPlainTextEdit{background-color: #212121; color: white; padding: 8;}")
        self.font = QFont()
        self.font.setFamily("Iosevka")
        self.font.setPointSize(12)
        self.text = None
        self.setFont(self.font)
        self.document_file = self.document()
        self.previousCommandLength = 0
        self.document_file.setDocumentMargin(-1)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        if self.movable is True:
            self.parent.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.movable is True:
            self.parent.mouseMoveEvent(event)

    def textUnderCursor(self):
        textCursor = self.textCursor()
        textCursor.select(QTextCursor.WordUnderCursor)

        return textCursor.selectedText()

    def keyPressEvent(self, e):
        cursor = self.textCursor()

        if self.parent:

            if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_A:
                return

            if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_Z:
                self.commandZPressed.emit("True")
                return

            if e.key() == 16777220:  # This is the ENTER key
                text = self.textCursor().block().text()

                if text == self.name + text.replace(self.name,
                                                    "") and text.replace(
                    self.name,
                    "") != "":  # This is to prevent adding in commands that were not meant to be added in
                    self.commands.append(text.replace(self.name, ""))
                self.commandSignal.emit(text)
                self.appendPlainText(self.name)

                return

            if e.key() == Qt.Key_Up:
                try:
                    if self.tracker != 0:
                        cursor.select(QTextCursor.BlockUnderCursor)
                        cursor.removeSelectedText()
                        self.appendPlainText(self.name)

                    self.insertPlainText(self.commands[self.tracker])
                    self.tracker += 1

                except IndexError:
                    self.tracker = 0

                return

            if e.key() == Qt.Key_Down:
                try:
                    cursor.select(QTextCursor.BlockUnderCursor)
                    cursor.removeSelectedText()
                    self.appendPlainText(self.name)

                    self.insertPlainText(self.commands[self.tracker])
                    self.tracker -= 1

                except IndexError:
                    self.tracker = 0

            if e.key() == 16777219:
                if cursor.positionInBlock() <= len(self.name):
                    return

                else:
                    cursor.deleteChar()

            super().keyPressEvent(e)

        e.accept()


class Terminal(QWidget):
    errorSignal = pyqtSignal(str)
    outputSignal = pyqtSignal(str)

    def __init__(self, parent, movable=False):
        super().__init__()

        self.setWindowFlags(
            Qt.Widget |
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint
        )
        self.movable = movable
        self.layout = QVBoxLayout()
        self.pressed = False
        self.process = QProcess()
        self.parent = parent
        self.name = None

        self.process.readyReadStandardError.connect(
            self.onReadyReadStandardError)
        self.process.readyReadStandardOutput.connect(
            self.onReadyReadStandardOutput)
        self.setLayout(self.layout)
        self.setStyleSheet("QWidget {background-color:invisible;}")

        # self.showMaximized() # comment this if you want to embed this widget

    def ispressed(self):
        return self.pressed

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def add(self):
        self.added()
        self.button = QPushButton("Hide terminal")
        self.button.setFont(QFont("Iosevka", 11))
        self.button.setStyleSheet("""
        height: 20;
        background-color: #212121;

        """)
        self.button.setFixedWidth(120)
        self.editor = PlainTextEdit(self, self.movable)
        self.highlighter = name_highlighter(self.editor.document(),
                                            str(getpass.getuser()),
                                            str(socket.gethostname()),
                                            str(os.getcwd()))
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.editor)
        self.editor.commandSignal.connect(self.handle)
        self.button.clicked.connect(self.remove)
        self.editor.commandZPressed.connect(self.handle)

    def added(self):
        self.pressed = True

    def remove(self):
        self.editor.deleteLater()
        self.button.deleteLater()
        self.parent.hideConsole()
        self.pressed = False

    def onReadyReadStandardError(self):
        self.error = self.process.readAllStandardError().data().decode()
        self.editor.appendPlainText(self.error.strip('\n'))
        self.errorSignal.emit(self.error)

    def onReadyReadStandardOutput(self):
        self.result = self.process.readAllStandardOutput().data().decode()
        self.editor.appendPlainText(self.result.strip('\n'))
        self.state = self.process.state()
        self.outputSignal.emit(self.result)

    def run(self, command):
        """Executes a system command."""
        if self.process.state() != 2:
            self.process.start(command)

    def handle(self, command):

        """Split a command into list so command echo hi would appear as ['echo', 'hi']"""
        real_command = command.replace(self.editor.name, "")

        if command == "True":
            if self.process.state() == 2:
                self.process.kill()
                self.editor.appendPlainText(
                    "Program execution killed, press enter")

        if real_command.startswith("python"):
            pass

        if real_command != "":
            command_list = real_command.split()
        else:
            command_list = None
        """Now we start implementing some commands"""
        if real_command == "clear":
            self.editor.clear()

        elif command_list is not None and command_list[0] == "echo":
            self.editor.appendPlainText(" ".join(command_list[1:]))

        elif real_command == "exit":
            self.remove()

        elif command_list is not None and command_list[0] == "cd" and len(
                command_list) > 1:
            try:
                os.chdir(" ".join(command_list[1:]))
                self.editor.name = "[" + str(getpass.getuser()) + "@" + str(
                    socket.gethostname()) + "]" + "  ~" + str(
                    os.getcwd()) + " >$ "
                if self.highlighter:
                    del self.highlighter
                self.highlighter = name_highlighter(self.editor.document(),
                                                    str(getpass.getuser()),
                                                    str(socket.gethostname()),
                                                    str(os.getcwd()))

            except FileNotFoundError as E:
                self.editor.appendPlainText(str(E))

        elif command_list is not None and len(command_list) == 1 and \
                command_list[0] == "cd":
            os.chdir(str(Path.home()))
            self.editor.name = "[" + str(getpass.getuser()) + "@" + str(
                socket.gethostname()) + "]" + "  ~" + str(
                os.getcwd()) + " >$ "

        elif self.process.state() == 2:
            self.process.write(real_command.encode())
            self.process.closeWriteChannel()

        elif command == self.editor.name + real_command:
            self.run(real_command)

        else:
            pass
    # When the user does a command like ls and then presses enter then it wont read the line where the cursor is on as a command


class name_highlighter(QSyntaxHighlighter):

    def __init__(self, parent=None, user_name=None, host_name=None, cwd=None):
        super().__init__(parent)
        self.highlightingRules = []
        self.name = user_name
        self.name2 = host_name
        self.cwd = cwd
        most_used = ["cd", "clear", "history", "ls", "man", "pwd", "what",
                     "type",
                     "strace", "ltrace", "gdb", "cat", "chmod", "cp", "chown",
                     "find", "grep", "locate", "mkdir",
                     "rmdir", "rm", "mv", "vim", "nano", "rename",
                     "touch", "wget", "zip", "tar", "gzip", "apt", "bg", "fg",
                     "df", "free", "ip", "jobs", "kill",
                     "killall", "mount", "umount", "ps", "sudo", "echo",
                     "top", "uname", "whereis", "uptime", "whereis", "whoami",
                     "exit"
                     ]  # most used linux commands, so we will highlight them!
        self.regex = {
            "class": "\\bclass\\b",
            "function": "[A-Za-z0-9_]+(?=\\()",
            "magic": "\\__[^']*\\__",
            "decorator": "@[^\n]*",
            "singleLineComment": "#[^\n]*",
            "quotation": "\"[^\"]*\"",
            "quotation2": "'[^\']*\'",
            "multiLineComment": "[-+]?[0-9]+",
            "int": "[-+]?[0-9]+",
        }
        """compgen -c returns all commands that you can run"""

        for f in most_used:
            nameFormat = QTextCharFormat()
            nameFormat.setForeground(QColor("#00ff00"))
            nameFormat.setFontItalic(True)
            self.highlightingRules.append(
                (QRegExp("\\b" + f + "\\b"), nameFormat))

        hostnameFormat = QTextCharFormat()
        hostnameFormat.setForeground(QColor("#12c2e9"))
        self.highlightingRules.append((QRegExp(self.name), hostnameFormat))
        self.highlightingRules.append((QRegExp(self.name2), hostnameFormat))

        otherFormat = QTextCharFormat()
        otherFormat.setForeground(QColor("#f7797d"))
        self.highlightingRules.append((QRegExp("~\/[^\s]*"), otherFormat))

        quotation1Format = QTextCharFormat()
        quotation1Format.setForeground(QColor("#96c93d"))
        self.highlightingRules.append((QRegExp("\"[^\"]*\""), quotation1Format))

        quotation2Format = QTextCharFormat()
        quotation2Format.setForeground(QColor("#96c93d"))
        self.highlightingRules.append((QRegExp("'[^\']*\'"), quotation2Format))

        integerFormat = QTextCharFormat()
        integerFormat.setForeground(QColor("#cc5333"))
        integerFormat.setFontItalic(True)
        self.highlightingRules.append(
            (QRegExp("\\b[-+]?[0-9]+\\b"), integerFormat))

    def highlightBlock(self, text):

        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class PythonThread(QThread):

    def __init__(self):
        super().__init__()
