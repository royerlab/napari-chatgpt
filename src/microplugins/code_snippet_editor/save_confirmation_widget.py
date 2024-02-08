from PyQt5.QtWidgets import QHBoxLayout, QWidget, QPushButton, QLabel, QSizePolicy


class SaveConfirmationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.save_callback = None
        self.discard_callback = None
        self.do_after_callable = None
        self.message_label = QLabel()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        self.message_label.setText("You have unsaved changes. Save before closing?")

        save_button = QPushButton("Save")
        discard_button = QPushButton("Discard")

        save_button.clicked.connect(self.onSave)
        discard_button.clicked.connect(self.onDiscard)

        layout.addWidget(self.message_label, 1)
        layout.addWidget(save_button)
        layout.addWidget(discard_button)

        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins if necessary
        self.setLayout(layout)

        # Set the vertical size policy to Minimum so it takes the least vertical space
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Attempt to directly control the widget's size
        self.setMaximumHeight(50)  # Adjust 100 to your needs

    def setCallbacks(self, save_callback, discard_callback, do_after_callable=None):
        self.save_callback = save_callback
        self.discard_callback = discard_callback
        self.do_after_callable = do_after_callable

    def setFilename(self, filename):
        self.message_label.setText(f"Save changes to '{filename}' before closing?")

    def onSave(self):
        if self.save_callback:
            self.save_callback()
        self.hide()
        if self.do_after_callable:
            self.do_after_callable()

    def onDiscard(self):
        if self.discard_callback:
            self.discard_callback()
        self.hide()
        if self.do_after_callable:
            self.do_after_callable()
