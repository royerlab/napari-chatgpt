from typing import Optional

from arbol import aprint
from qtpy.QtWidgets import QHBoxLayout, QWidget, QPushButton, QLabel, \
    QSizePolicy, QLineEdit, QTextEdit


class TextInputWidget(QWidget):
    def __init__(self,
                 max_height: int = 50,
                 margin: int = 0,
                 parent=None):

        super().__init__(parent=parent)

        # Initialize callbacks:
        self.enter_callback = None
        self.cancel_callback = None
        self.do_after_callable = None

        #
        self.multi_line = False

        # Initialize widgets:
        self.initUI(max_height=max_height,
                    margin=margin)

    def initUI(self,
               max_height: int,
               margin: int):

        # Layout:
        self.layout = QHBoxLayout(self)

        # Message label:
        self.message_label = QLabel()
        self.layout.addWidget(self.message_label)

        # Input fields (both single-line and multi-line, hidden by default):
        self.single_line_input = QLineEdit()
        self.single_line_input.setPlaceholderText("Enter text here")
        self.single_line_input.setSizePolicy(QSizePolicy.Expanding,
                                             QSizePolicy.Preferred)
        self.single_line_input.returnPressed.connect(self.on_enter)
        self.layout.addWidget(self.single_line_input)

        self.multi_line_input = QTextEdit()
        self.multi_line_input.setPlaceholderText("Enter text here")
        self.multi_line_input.setSizePolicy(QSizePolicy.Expanding,
                                            QSizePolicy.Preferred)
        self.layout.addWidget(self.multi_line_input)
        self.multi_line_input.hide()  # Initially hidden

        # Buttons:
        self.enter_button = QPushButton('Enter')
        self.enter_button.clicked.connect(self.on_enter)
        self.layout.addWidget(self.enter_button)

        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.on_cancel)
        self.layout.addWidget(self.cancel_button)

        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.setMaximumHeight(max_height)
        self.hide()


    def show_input(self, message: str,
                   placeholder_text: str = "Enter input here",
                   default_text: str = '',
                   enter_text: str = "Enter",
                   cancel_text: str = "Cancel",
                   enter_callback=None,
                   cancel_callback=None,
                   do_after_callable=None,
                   multi_line: bool = False,
                   max_height: Optional[int] = None):

        # Set multi_line:
        self.multi_line = multi_line

        # Set the maximum height if provided:
        if max_height:
            self.setMaximumHeight(max_height)

        # Hide both inputs initially:
        self.single_line_input.hide()
        self.multi_line_input.hide()

        # Determine which input field to show based on multi_line:
        if multi_line:
            self.current_input = self.multi_line_input
        else:
            self.current_input = self.single_line_input

        # Configure the chosen input field and show it:
        self.current_input.setText(default_text)
        self.current_input.setPlaceholderText(placeholder_text)
        self.current_input.show()

        # Update labels and buttons:
        self.message_label.setText(message)
        self.enter_button.setText(enter_text)
        self.cancel_button.setText(cancel_text)

        # Show or hide the cancel button based on cancel_text:
        if cancel_text:
            self.cancel_button.show()
        else:
            self.cancel_button.hide()

        # Set the callbacks:
        self.enter_callback = enter_callback
        self.cancel_callback = cancel_callback
        self.do_after_callable = do_after_callable

        # Show the widget:
        self.show()

    def on_enter(self):
        input_text = self.current_input.text() if not self.multi_line else self.current_input.toPlainText()
        try:
            if self.enter_callback:
                self.enter_callback(input_text)
        except Exception as e:
            aprint(f'Error in on_enter: {e}')
            import traceback
            traceback.print_exc()
        finally:
            self.hide()
            if self.do_after_callable:
                self.do_after_callable(input_text)

    def on_cancel(self):
        try:
            if self.cancel_callback:
                self.cancel_callback('')
        except Exception as e:
            aprint(f'Error in on_enter: {e}')
            import traceback
            traceback.print_exc()
        finally:
            self.hide()
            if self.do_after_callable:
                self.do_after_callable('')


