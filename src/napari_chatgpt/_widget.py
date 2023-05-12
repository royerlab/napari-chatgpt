"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
import sys
from typing import TYPE_CHECKING

import openai
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QComboBox
from napari.viewer import Viewer
from qtpy.QtWidgets import QPushButton, QWidget

if TYPE_CHECKING:
    pass

from arbol import aprint


class OmegaQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        # Create a QVBoxLayout instance
        self.layout = QVBoxLayout()

        self._model_selection()

        self._memory_type_selection()

        self._personality_selection()

        # Start Omega button:
        self.start_omega_button = QPushButton("Start Omega")
        self.start_omega_button.clicked.connect(self._on_click)

        # Omega button:
        self.layout.addWidget(self.start_omega_button)

        # Set the layout on the application's window
        self.setLayout(self.layout)

    def _personality_selection(self):
        # Create a QLabel instance
        self.agent_personality_label = QLabel("Select a personality:")
        # Add the label to the layout
        self.layout.addWidget(self.agent_personality_label)
        # Create a QComboBox instance
        self.agent_personality_combo_box = QComboBox()
        # Add characters:
        self.agent_personality_combo_box.addItem('neutral')
        self.agent_personality_combo_box.addItem('prof')
        self.agent_personality_combo_box.addItem('mobster')
        # Add the combo box to the layout
        self.layout.addWidget(self.agent_personality_combo_box)

    def _memory_type_selection(self):
        # Create a QLabel instance
        self.memory_type_label = QLabel("Select a memory type:")
        # Add the label to the layout
        self.layout.addWidget(self.memory_type_label)
        # Create a QComboBox instance
        self.memory_type_combo_box = QComboBox()
        # Add memory types:
        self.memory_type_combo_box.addItem('standard')
        self.memory_type_combo_box.addItem('summarising')
        # Add the combo box to the layout
        self.layout.addWidget(self.memory_type_combo_box)

    def _model_selection(self):
        # Create a QLabel instance
        self.model_label = QLabel("Select a model:")
        # Add the label to the layout
        self.layout.addWidget(self.model_label)
        # Create a QComboBox instance
        self.model_combo_box = QComboBox()
        # Add items to the combo box
        for model in openai.Model.list().data:
            model_id = model.openai_id
            if 'gpt' in model_id:
                self.model_combo_box.addItem(model_id)
        # Connect the activated signal to a slot
        # self.model_combo_box.activated[str].connect(self.onActivated)
        # Add the combo box to the layout
        self.layout.addWidget(self.model_combo_box)

    def _on_click(self):
        aprint("Starting Omega!")

        from napari_chatgpt.chat_server.chat_server import start_chat_server
        start_chat_server(self.viewer,
                          llm_model_name=self.model_combo_box.currentText(),
                          memory_type=self.memory_type_combo_box.currentText(),
                          agent_personality= self.agent_personality_combo_box.currentText())




def main():
    app = QApplication(sys.argv)

    # You need to create an instance of napari.viewer.Viewer
    # I'm creating a dummy instance here, replace it with a real instance if needed
    viewer = Viewer()

    widget = OmegaQWidget(viewer)
    widget.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()