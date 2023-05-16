"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
import sys
from typing import TYPE_CHECKING

import openai
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QComboBox
from napari.viewer import Viewer
from qtpy.QtWidgets import QPushButton, QWidget

from napari_chatgpt.utils.python.installed_packages import is_package_installed

if TYPE_CHECKING:
    pass

from arbol import aprint

_creativity_mapping = {}
_creativity_mapping['uncreative'] = 0.1
_creativity_mapping['slightly creative'] = 0.3
_creativity_mapping['moderately creative'] = 0.5
_creativity_mapping['creative'] = 0.7
_creativity_mapping['highly creative'] = 0.9
_creativity_mapping['lsd'] = 1.0


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

        self.layout.setAlignment(Qt.AlignTop)

        self._model_selection()

        # Create a QLabel instance
        self.creativity_label = QLabel("Chose the level of creativity:")

        # Add the label to the layout
        self.layout.addWidget(self.creativity_label)

        # Temperature field:
        self.creativity_combo_box = QComboBox()

        # Add values:
        self.creativity_combo_box.addItem('uncreative')
        self.creativity_combo_box.addItem('slightly creative')
        self.creativity_combo_box.addItem('moderately creative')
        self.creativity_combo_box.addItem('creative')
        self.creativity_combo_box.addItem('highly creative')
        self.creativity_combo_box.addItem('lsd')

        # Add the temperature field to the layout:
        self.layout.addWidget(self.creativity_combo_box)

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

        # Add OpenAI models to the combo box:
        for model in openai.Model.list().data:
            model_id = model.openai_id
            if 'gpt' in model_id:
                self.model_combo_box.addItem(model_id)

        # if is_package_installed('googlebard'):
        self.model_combo_box.addItem('bard')

        if is_package_installed('anthropic'):
            # Add Anthropic models to the combo box:
            self.model_combo_box.addItem('claude-v1')
            self.model_combo_box.addItem('claude-v1-100k')
            self.model_combo_box.addItem('claude-instant-v1')
            self.model_combo_box.addItem('claude-instant-v1-100k')
            self.model_combo_box.addItem('claude-v1.3')
            self.model_combo_box.addItem('claude-v1.3-100k')
            self.model_combo_box.addItem('claude-instant-v1.1')
            self.model_combo_box.addItem('claude-instant-v1.1-100k')

        if is_package_installed('pygpt4all'):
            self.model_combo_box.addItem('ggml-mpt-7b-chat')
            self.model_combo_box.addItem('ggml-gpt4all-j-v1.3-groovy')
            self.model_combo_box.addItem('ggml-gpt4all-l13b-snoozy')

        # Connect the activated signal to a slot
        # self.model_combo_box.activated[str].connect(self.onActivated)
        # Add the combo box to the layout
        self.layout.addWidget(self.model_combo_box)

    def _on_click(self):
        aprint("Starting Omega!")

        from napari_chatgpt.chat_server.chat_server import start_chat_server
        start_chat_server(self.viewer,
                          llm_model_name=self.model_combo_box.currentText(),
                          temperature=float(_creativity_mapping[
                                                self.creativity_combo_box.currentText()]),
                          memory_type=self.memory_type_combo_box.currentText(),
                          agent_personality=self.agent_personality_combo_box.currentText())


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
