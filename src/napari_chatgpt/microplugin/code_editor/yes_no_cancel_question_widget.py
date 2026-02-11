"""Inline Yes/No/Cancel question widget for user confirmation prompts."""

from arbol import aprint
from qtpy.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget


class YesNoCancelQuestionWidget(QWidget):
    """An inline widget that displays a question with Yes, No, and Cancel buttons.

    Hidden by default. Call ``show_question()`` to display a message and
    register callbacks. The widget auto-hides after any button is pressed.

    Attributes:
        yes_callback: Callable invoked when Yes is clicked.
        no_callback: Callable invoked when No is clicked.
        cancel_callback: Callable invoked when Cancel is clicked.
        do_after_callable: Optional callable invoked after any button action.
    """

    def __init__(self, max_height: int = 50, margin: int = 0, parent=None):
        """Initialize the question widget.

        Args:
            max_height: Maximum widget height in pixels.
            margin: Layout margin in pixels.
            parent: Parent widget.
        """

        super().__init__(parent=parent)

        # Initialize callbacks:
        self.yes_callback = None
        self.no_callback = None
        self.cancel_callback = None
        self.do_after_callable = None

        # Initialize widgets:
        self.initUI(max_height=max_height, margin=margin)

    def initUI(self, max_height: int, margin: int):
        """Build the UI with a message label and Yes/No/Cancel buttons."""
        layout = QHBoxLayout()

        # Set message:
        self.message_label = QLabel()
        self.message_label.setText("")

        # Buttons:
        self.yes_button = QPushButton("")
        self.no_button = QPushButton("")
        self.cancel_button = QPushButton("")

        # Connect buttons to callbacks:
        self.yes_button.clicked.connect(self.on_yes)
        self.no_button.clicked.connect(self.on_no)
        self.cancel_button.clicked.connect(self.on_cancel)

        # Add widgets to layout:
        layout.addWidget(self.message_label, 1)
        layout.addWidget(self.yes_button)
        layout.addWidget(self.no_button)
        layout.addWidget(self.cancel_button)

        layout.setContentsMargins(
            margin, margin, margin, margin
        )  # Reduce margins if necessary
        self.setLayout(layout)

        # Set the vertical size policy to Minimum so it takes the least vertical space
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Attempt to directly control the widget's size
        self.setMaximumHeight(max_height)  # Adjust 100 to your needs

        # Hide the widget initially:
        self.hide()

    def show_question(
        self,
        message: str,
        yes_text: str = "Yes",
        no_text: str = "No",
        cancel_text: str | None = "Cancel",
        yes_callback=None,
        no_callback=None,
        cancel_callback=None,
        do_after_callable=None,
    ):
        """Configure and display the question widget.

        Args:
            message: The question text to display.
            yes_text: Label for the Yes button.
            no_text: Label for the No button.
            cancel_text: Label for the Cancel button. If None, the Cancel
                button is hidden.
            yes_callback: Called when Yes is clicked.
            no_callback: Called when No is clicked.
            cancel_callback: Called when Cancel is clicked.
            do_after_callable: Called after any button's callback completes.
        """

        self.message_label.setText(message)
        self.yes_button.setText(yes_text)
        self.no_button.setText(no_text)

        if cancel_text:
            self.cancel_button.setText(cancel_text)
            self.cancel_button.show()
        else:
            self.cancel_button.hide()

        self.yes_callback = yes_callback
        self.no_callback = no_callback
        self.cancel_callback = cancel_callback
        self.do_after_callable = do_after_callable
        self.show()

    def on_yes(self):
        """Invoke the yes callback, then hide the widget."""
        try:
            if self.yes_callback:
                self.yes_callback()
        except Exception as e:
            aprint(f"Error in on_yes: {e}")
            import traceback

            traceback.print_exc()
        finally:
            self.hide()
            if self.do_after_callable:
                self.do_after_callable()

    def on_no(self):
        """Invoke the no callback, then hide the widget."""
        try:
            if self.no_callback:
                self.no_callback()
        except Exception as e:
            aprint(f"Error in on_no: {e}")
            import traceback

            traceback.print_exc()
        finally:
            self.hide()
            if self.do_after_callable:
                self.do_after_callable()

    def on_cancel(self):
        """Invoke the cancel callback, then hide the widget."""
        try:
            if self.cancel_callback:
                self.cancel_callback()
        except Exception as e:
            aprint(f"Error in on_cancel: {e}")
            import traceback

            traceback.print_exc()
        finally:
            self.hide()
            if self.do_after_callable:
                self.do_after_callable()
