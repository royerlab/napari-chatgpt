"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
import sys
from typing import TYPE_CHECKING, List

from napari_chatgpt.chat_server.chat_server import NapariChatServer
from napari_chatgpt.utils.api_keys.api_key import set_api_key
from napari_chatgpt.utils.ollama.ollama import is_ollama_running, \
    get_ollama_models
from napari_chatgpt.utils.python.installed_packages import \
    is_package_installed
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QCheckBox
from PyQt5.QtWidgets import QVBoxLayout, QComboBox
from napari.viewer import Viewer
from qtpy.QtWidgets import QPushButton, QWidget




if TYPE_CHECKING:
    pass

from arbol import aprint, asection

_creativity_mapping = {}
_creativity_mapping['normal'] = 0.0
_creativity_mapping['slightly creative'] = 0.01
_creativity_mapping['moderately creative'] = 0.05
_creativity_mapping['creative'] = 0.1


class OmegaQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        aprint("OmegaQWidget instantiated!")

        # Napari viewer instance:
        self.viewer = napari_viewer

        # Napari chat server instance:
        self.server: NapariChatServer = None

        # Create a QVBoxLayout instance
        self.layout = QVBoxLayout()

        # Set layout alignment:
        self.layout.setAlignment(Qt.AlignTop)

        # Add elements to UI:
        self._model_selection()
        self._creativity_level()
        self._memory_type_selection()
        self._personality_selection()
        self._fix_imports()
        self._fix_bad_version_calls()
        self._install_missing_packages()
        self._autofix_mistakes()
        self._autofix_widgets()
        self._verbose()

        self._start_omega_button()

        # Set the layout on the application's window
        self.setLayout(self.layout)

    def _model_selection(self):
        aprint("Setting up model selection UI.")

        # Create a QLabel instance
        self.model_label = QLabel("Select a model:")
        # Add the label to the layout
        self.layout.addWidget(self.model_label)
        # Create a QComboBox instance
        self.model_combo_box = QComboBox()
        # Set tooltip for the combo box
        self.model_combo_box.setToolTip(
            "Choose an LLM model. Best models are GPT4 and GPT3.5, \n"
            "with Claude a bit behind, other models are experimental\n"
            "and unfortunately barely usable. WARNING: recent GPT models\n"
            "have poor coding performance (0613), avoid them!\n"
            "Models at the top of list are better!")

        # Model list:
        model_list: List[str] = []

        # Add OpenAI models to the combo box:
        with asection(f"Enumerating all OpenAI ChatGPT models:"):
            set_api_key('OpenAI')

            from openai import OpenAI
            client = OpenAI()

            for model in client.models.list().data:
                model_id = model.id
                if 'gpt' in model_id:
                    aprint(model_id)
                    model_list.append(model_id)


        if is_package_installed('anthropic'):
            # Add Anthropic models to the combo box:
            model_list.append('claude-2')
            model_list.append('claude-instant-1')


        if is_ollama_running():
            ollama_models = get_ollama_models()
            for ollama_model in ollama_models:
                model_list.append('ollama_'+ollama_model)

        # Postprocess list:
        # Ensure that some 'bad' models are at the end of the list:
        bad_models = [m for m in model_list if '0613' in m]
        for bad_model in bad_models:
            if bad_model in model_list:
                model_list.remove(bad_model)
                model_list.append(bad_model)

        # Ensure that the best models are at the top of the list:
        best_models = [m for m in model_list if '0314' in m or '0301' in m or '1106' in m]
        model_list = best_models + [m for m in model_list if m not in best_models]

        # normalise list:
        model_list = list(model_list)

        # Add models to combo box:
        for model in model_list:
            self.model_combo_box.addItem(model)

        # Connect the activated signal to a slot
        # self.model_combo_box.activated[str].connect(self.onActivated)
        # Add the combo box to the layout
        self.layout.addWidget(self.model_combo_box)

    def _creativity_level(self):
        aprint("Setting up creativity level UI.")

        # Create a QLabel instance
        self.creativity_label = QLabel("Chose the level of creativity:")
        # Add the label to the layout
        self.layout.addWidget(self.creativity_label)
        # Creativity combobox:
        self.creativity_combo_box = QComboBox()
        self.creativity_combo_box.setToolTip(
            "Choose the level of creativity of Omega\n"
            "The less creative the more deterministic\n"
            "and accurate the results.\n"
            "Teh more creative, the more fantasy and\n"
            "the less competent it is at code generation\n"
            "and precise reasoning.")
        # Add values:
        self.creativity_combo_box.addItem('normal')
        self.creativity_combo_box.addItem('slightly creative')
        self.creativity_combo_box.addItem('moderately creative')
        self.creativity_combo_box.addItem('creative')
        self.creativity_combo_box.setCurrentIndex(0)
        # Add the creativity combobox to the layout:
        self.layout.addWidget(self.creativity_combo_box)

    def _memory_type_selection(self):
        aprint("Setting up memory type UI.")

        # Create a QLabel instance
        self.memory_type_label = QLabel("Select a memory type:")
        # Add the label to the layout
        self.layout.addWidget(self.memory_type_label)
        # Create a QComboBox instance
        self.memory_type_combo_box = QComboBox()
        self.memory_type_combo_box.setToolTip(
            "'hybrid' is best as it combines accurate short-term memory \n"
            "with summarised long term memory. 'bounded' only remembers \n"
            "the last few messages. 'infinite' remembers everything.")
        # Add memory types:
        self.memory_type_combo_box.addItem('hybrid')
        self.memory_type_combo_box.addItem('bounded')
        self.memory_type_combo_box.addItem('infinite')
        # Add the combo box to the layout
        self.layout.addWidget(self.memory_type_combo_box)

    def _personality_selection(self):
        aprint("Setting up personality UI.")

        # Create a QLabel instance
        self.agent_personality_label = QLabel("Select a personality:")
        # Add the label to the layout
        self.layout.addWidget(self.agent_personality_label)
        # Create a QComboBox instance
        self.agent_personality_combo_box = QComboBox()
        self.agent_personality_combo_box.setToolTip(
            "Personalities affect the style of the answers\n"
            "but (hopefully) not their quality")
        # Add characters:
        self.agent_personality_combo_box.addItem('coder')
        self.agent_personality_combo_box.addItem('neutral')
        self.agent_personality_combo_box.addItem('prof')
        self.agent_personality_combo_box.addItem('mobster')
        self.agent_personality_combo_box.addItem('yoda')
        # Add the combo box to the layout
        self.layout.addWidget(self.agent_personality_combo_box)

    def _fix_imports(self):
        aprint("Setting up fix imports UI.")

        # Create a QLabel instance
        self.fix_imports_checkbox = QCheckBox("Fix missing imports")
        self.fix_imports_checkbox.setChecked(True)
        self.fix_imports_checkbox.setToolTip(
            "Uses LLM to check for missing imports.\n"
            "This involves a LLM call which can incur additional\n"
            "cost in time and possibly money."
        )
        # Add the fix_imports checkbox to the layout:
        self.layout.addWidget(self.fix_imports_checkbox)

    def _fix_bad_version_calls(self):
        aprint("Setting up bad version imports UI.")

        # Create a QLabel instance
        self.fix_bad_calls_checkbox = QCheckBox("Fix bad function calls")
        self.fix_bad_calls_checkbox.setChecked(True)
        self.fix_bad_calls_checkbox.setToolTip("Uses LLM to fix function calls.\n"
                                              "When turned on, this detects wrong function calls, \n"
                                              "possibly because of library version mismatch and fixes,"
                                              "replaces the offending code with the right version! "
                                              "This involves a LLM call which can incurr additional\n"
                                              "cost in time and possibly money."
                                               )
        # Add the fix_code checkbox to the layout:
        self.layout.addWidget(self.fix_bad_calls_checkbox)

    def _install_missing_packages(self):
        aprint("Setting up install missing packages UI.")

        # Create a QLabel instance
        self.install_missing_packages_checkbox = QCheckBox(
            "Install missing packages")
        self.install_missing_packages_checkbox.setChecked(True)
        self.install_missing_packages_checkbox.setToolTip(
            "Uses LLM to figure out which packages to install.\n"
            "This involves a LLM call which can incur additional\n"
            "cost in time and possibly money.")
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.install_missing_packages_checkbox)

    def _autofix_mistakes(self):
        aprint("Setting up autofix mistakes UI.")

        # Create a QLabel instance
        self.autofix_mistakes_checkbox = QCheckBox(
            "Autofix coding mistakes")
        self.autofix_mistakes_checkbox.setChecked(False)
        self.autofix_mistakes_checkbox.setToolTip(
            "When checked Omega will try to fix on its own coding mistakes\n"
            "when processing data and interacting with the napari viewer.\n"
            "This does not include making widgets!\n"
            "Works so-so with ChatGPT 3.5, but works well with ChatGPT 4.\n"
            "This involves a LLM call which can incur additional\n"
            "cost in time and possibly money.")
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.autofix_mistakes_checkbox)

    def _autofix_widgets(self):
        aprint("Setting up autofix widgets UI.")

        # Create a QLabel instance
        self.autofix_widgets_checkbox = QCheckBox(
            "Autofix widget coding mistakes")
        self.autofix_widgets_checkbox.setChecked(False)
        self.autofix_widgets_checkbox.setToolTip(
            "When checked Omega will try to fix its own \n"
            "coding mistakes when making widgets. \n"
            "Works so-so with ChatGPT 3.5, but works well with ChatGPT 4.\n"
            "This involves a LLM call which can incur additional\n"
            "cost in time and possibly money.")
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.autofix_widgets_checkbox)

    def _verbose(self):
        aprint("Setting up verbose UI.")

        # Create a QLabel instance
        self.verbose_checkbox = QCheckBox(
            "High console verbosity")
        self.verbose_checkbox.setChecked(False)
        self.verbose_checkbox.setToolTip(
            "High level of verbosity in the console\n"
            "This includes a lot of internal logging\n"
            "from the langchain library.\n"
            "Nearly incomprehensible, but usefull\n"
            "if you are interested to see the prompts\n"
            "in action...")
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.verbose_checkbox)

    def _start_omega_button(self):
        aprint("Setting up start Omega button UI.")

        # Start Omega button:
        self.start_omega_button = QPushButton("Start Omega")
        self.start_omega_button.clicked.connect(self._on_click)
        self.start_omega_button.setToolTip(
            "Start Omega, this will open a browser window.\n"
            "You can restart Omega with new settings by\n"
            "clicking again this button. This closes the\n"
            "previous session.")
        # Omega button:
        self.layout.addWidget(self.start_omega_button)

    def _on_click(self):
        aprint("Starting Omega now!")

        # Stop previous instance if it exists:
        if self.server:
            self.server.stop()

        # Temperature:
        temperature = float(_creativity_mapping[
                                self.creativity_combo_box.currentText()])
        tool_temperature = 0.1*temperature

        from napari_chatgpt.chat_server.chat_server import start_chat_server
        self.server = start_chat_server(self.viewer,
                                        llm_model_name=self.model_combo_box.currentText(),
                                        temperature=temperature,
                                        tool_temperature=tool_temperature,
                                        memory_type=self.memory_type_combo_box.currentText(),
                                        agent_personality=self.agent_personality_combo_box.currentText(),
                                        fix_imports=self.fix_imports_checkbox.isChecked(),
                                        install_missing_packages=self.install_missing_packages_checkbox.isChecked(),
                                        fix_bad_calls=self.fix_bad_calls_checkbox.isChecked(),
                                        autofix_mistakes=self.autofix_mistakes_checkbox.isChecked(),
                                        autofix_widget=self.autofix_widgets_checkbox.isChecked(),
                                        verbose=self.verbose_checkbox.isChecked()
                                        )


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
