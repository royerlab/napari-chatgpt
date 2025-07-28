"""
napari_chatgpt OmegaQWidget

# OmegaQWidget.py

"""

import sys
import traceback
from typing import TYPE_CHECKING, List

from napari.viewer import Viewer
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QLabel, QCheckBox
from qtpy.QtWidgets import QPushButton, QWidget
from qtpy.QtWidgets import QVBoxLayout, QComboBox

from napari_chatgpt.llm.litemind_api import get_model_list
from napari_chatgpt.microplugin.microplugin_window import MicroPluginMainWindow
from napari_chatgpt.utils.configuration.app_configuration import AppConfiguration
from napari_chatgpt.utils.qt.one_time_disclaimer_dialog import (
    show_one_time_disclaimer_dialog,
)

if TYPE_CHECKING:
    pass

from arbol import aprint, asection

_creativity_mapping = {}
_creativity_mapping["normal"] = 0.0
_creativity_mapping["slightly creative"] = 0.01
_creativity_mapping["moderately creative"] = 0.05
_creativity_mapping["creative"] = 0.1

# Ensure the singleton pattern is on:
MicroPluginMainWindow._singleton_pattern_active = True


class OmegaQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer, add_code_editor=True):
        super().__init__()
        aprint("OmegaQWidget instantiated!")

        # Get app configuration:
        self.config = AppConfiguration("omega")

        # Napari viewer instance:
        self.viewer = napari_viewer

        # Napari chat server instance:
        # from napari_chatgpt.chat_server.chat_server import NapariChatServer
        self.server: "NapariChatServer" = None

        # Create a QVBoxLayout instance
        self.layout = QVBoxLayout()

        # Set layout alignment:
        self.layout.setAlignment(Qt.AlignTop)

        with asection("Setting up OmegaQWidget UI:"):

            # Add elements to UI:
            self._main_model_selection()
            self._tool_model_selection()
            self._creativity_level()
            # self._memory_type_selection()
            self._personality_selection()
            self._fix_imports()
            self._fix_bad_version_calls()
            self._install_missing_packages()
            self._autofix_mistakes()
            self._autofix_widgets()
            self._builtin_websearch_tool()
            self._tutorial_mode()
            self._save_chats_as_notebooks()
            self._verbose()

            # Instantiate the MicroPluginMainWindow:
            if add_code_editor:
                self.micro_plugin_main_window = MicroPluginMainWindow(
                    napari_viewer=napari_viewer
                )

            # Add the start Omega:
            self._start_omega_button()

            # Add the show editor button:
            if add_code_editor:
                self._show_editor_button()

            # Set the layout on the application's window
            self.setLayout(self.layout)

        # Make sure that when the viewer window closes this widget closes too:
        try:
            self.viewer.window._qt_window.destroyed.connect(self.close)
        except Exception as e:
            aprint(f"Error: {e}")
            aprint("Could not connect to viewer's closed signal.")
            traceback.print_exc()

    def _main_model_selection(self):

        aprint("Setting up main model selection UI.")

        # Create a QLabel instance
        self.model_label = QLabel("Select a main model:")
        # Add the label to the layout
        self.layout.addWidget(self.model_label)
        # Create a QComboBox instance
        self.main_model_combo_box = QComboBox()
        # Set tooltip for the combo box
        self.main_model_combo_box.setToolTip(
            "Choose the main LLM model used for conversation. \n"
        )

        # Add All litemind API models to the combo box:
        model_list: List[str] = list(get_model_list())

        # Filter and sort the models to have preferred models first:
        self._prefered_models(model_list)

        # Add models to combo box:
        for model in model_list:
            self.main_model_combo_box.addItem(model)

        # Add the combo box to the layout
        self.layout.addWidget(self.main_model_combo_box)

    def _tool_model_selection(self):

        aprint("Setting up tool model selection UI.")

        # Create a QLabel instance
        self.model_label = QLabel("Select a coding model:")
        # Add the label to the layout
        self.layout.addWidget(self.model_label)
        # Create a QComboBox instance
        self.tool_model_combo_box = QComboBox()
        # Set tooltip for the combo box
        self.tool_model_combo_box.setToolTip(
            "Choose the tool LLM model used for coding. \n"
        )

        # Add All litemind API models to the combo box:
        model_list: List[str] = list(get_model_list())

        # Filter and sort the models to have preferred models first:
        self._prefered_models(model_list)

        # Add models to combo box:
        for model in model_list:
            self.tool_model_combo_box.addItem(model)

        # Add the combo box to the layout
        self.layout.addWidget(self.tool_model_combo_box)

    @staticmethod
    def _prefered_models(model_list: List[str]):
        # List of filters to identify preferred models:
        preferred_models_filter = [
            "gpt-4.1",
            "gpt-4o",
        ]  # , 'claude-3-7', 'opus-4', 'gemini-2.5-pro']
        # List of preferred models:
        preferred_models = [
            model
            for model in model_list
            if any(filter in model for filter in preferred_models_filter)
        ]
        # Exclude models that are in fact not preferred::
        preferred_models.remove("chatgpt-4o-latest")
        # Sort the model list stably to have preferred models first:
        model_list.sort(key=lambda x: (x not in preferred_models, x))

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
            "The more creative, the more fantasy and\n"
            "the less competent it is at code generation\n"
            "and precise reasoning."
        )
        # Add values:
        self.creativity_combo_box.addItem("normal")
        self.creativity_combo_box.addItem("slightly creative")
        self.creativity_combo_box.addItem("moderately creative")
        self.creativity_combo_box.addItem("creative")
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
            "the last few messages. 'infinite' remembers everything."
        )
        # Add memory types:
        self.memory_type_combo_box.addItem("hybrid")
        self.memory_type_combo_box.addItem("bounded")
        self.memory_type_combo_box.addItem("infinite")
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
            "but (hopefully) not their quality"
        )
        # Add characters:
        self.agent_personality_combo_box.addItem("genius")
        self.agent_personality_combo_box.addItem("coder")
        self.agent_personality_combo_box.addItem("neutral")
        self.agent_personality_combo_box.addItem("prof")
        self.agent_personality_combo_box.addItem("mobster")
        self.agent_personality_combo_box.addItem("yoda")
        # Add the combo box to the layout
        self.layout.addWidget(self.agent_personality_combo_box)

    def _fix_imports(self):
        aprint("Setting up fix imports UI.")

        # Get app configuration:
        config = AppConfiguration("omega")

        # Create a QLabel instance
        self.fix_imports_checkbox = QCheckBox("Fix missing imports")
        self.fix_imports_checkbox.setChecked(config.get("fix_missing_imports", False))
        self.fix_imports_checkbox.setToolTip(
            "Uses LLM to check for missing imports.\n"
            "This involves a LLM call which can incur additional\n"
            "cost in time and possibly money."
        )
        # Add the fix_imports checkbox to the layout:
        self.layout.addWidget(self.fix_imports_checkbox)

    def _fix_bad_version_calls(self):
        aprint("Setting up bad version imports UI.")

        # Get app configuration:
        config = AppConfiguration("omega")

        # Create a QLabel instance
        self.fix_bad_calls_checkbox = QCheckBox("Fix bad function calls")
        self.fix_bad_calls_checkbox.setChecked(config.get("fix_bad_calls", False))
        self.fix_bad_calls_checkbox.setToolTip(
            "Uses LLM to fix function calls.\n"
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

        # Get app configuration:
        config = AppConfiguration("omega")

        # Create a QLabel instance
        self.install_missing_packages_checkbox = QCheckBox("Install missing packages")
        self.install_missing_packages_checkbox.setChecked(
            config.get("install_missing_packages", False)
        )
        self.install_missing_packages_checkbox.setToolTip(
            "Uses LLM to figure out which packages to install.\n"
            "This involves a LLM call which can incur additional\n"
            "cost in time and possibly money."
        )
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.install_missing_packages_checkbox)

    def _autofix_mistakes(self):
        aprint("Setting up autofix mistakes UI.")

        # Get app configuration:
        config = AppConfiguration("omega")

        # Create a QLabel instance
        self.autofix_mistakes_checkbox = QCheckBox("Autofix coding mistakes")
        self.autofix_mistakes_checkbox.setChecked(config.get("autofix_mistakes", True))
        self.autofix_mistakes_checkbox.setToolTip(
            "When checked Omega will try to fix on its own coding mistakes\n"
            "when processing data and interacting with the napari viewer.\n"
            "This does not include making widgets!\n"
            "This involves a LLM call which can incur additional\n"
            "cost in time and possibly money."
        )
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.autofix_mistakes_checkbox)

    def _autofix_widgets(self):
        aprint("Setting up autofix widgets UI.")

        # Get app configuration:
        config = AppConfiguration("omega")

        # Create a QLabel instance
        self.autofix_widgets_checkbox = QCheckBox("Autofix widget coding mistakes")
        self.autofix_widgets_checkbox.setChecked(config.get("autofix_widgets", True))
        self.autofix_widgets_checkbox.setToolTip(
            "When checked Omega will try to fix its own \n"
            "coding mistakes when making widgets. \n"
            "Works so-so with ChatGPT 3.5, but works well with ChatGPT 4.\n"
            "This requires API calls which may incur additional\n"
            "cost in time and possibly money."
        )
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.autofix_widgets_checkbox)

    def _tutorial_mode(self):
        aprint("Setting up tutorial mode UI.")

        # Get app configuration:
        config = AppConfiguration("omega")

        # Create a QLabel instance
        self.tutorial_mode_checkbox = QCheckBox("Tutorial/Didactic mode")
        self.tutorial_mode_checkbox.setChecked(
            config.get("tutorial_mode_checkbox", False)
        )
        self.tutorial_mode_checkbox.setToolTip(
            "When checked Omega will actively asks questions \n"
            "to clarify and disambiguate the request, will propose \n"
            "multiple options and try to be as didactic as possible. "
        )
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.tutorial_mode_checkbox)

    def _builtin_websearch_tool(self):
        aprint("Setting up builtin web search UI.")

        # Get app configuration:
        config = AppConfiguration("omega")

        # Create a QLabel instance
        self.builtin_websearch_tool_checkbox = QCheckBox("Web search tool")
        self.builtin_websearch_tool_checkbox.setChecked(
            config.get("builtin_websearch_tool", True)
        )
        self.builtin_websearch_tool_checkbox.setToolTip(
            "When checked Omega will use a web search tool \n"
            "to search the web for information to answer your questions.\n"
            "This is useful when Omega does not know the answer to your question.\n"
            "Note: This is for built-in web search only!\n"
            "This is not supported by all models, \n"
        )
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.builtin_websearch_tool_checkbox)

    def _save_chats_as_notebooks(self):
        aprint("Setting up save notebooks UI.")

        # Get app configuration:
        config = AppConfiguration("omega")

        # Create a QLabel instance
        self.save_chats_as_notebooks = QCheckBox("Save chats as Jupyter notebooks")
        self.save_chats_as_notebooks.setChecked(
            config.get("save_chats_as_notebooks", True)
        )
        self.save_chats_as_notebooks.setToolTip(
            "When checked Omega will save the chats as Jupyter notebooks \n"
            "by default in a folder on the user's desktop."
        )
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.save_chats_as_notebooks)

    def _verbose(self):
        aprint("Setting up verbose UI.")

        # Get app configuration:
        config = AppConfiguration("omega")

        # Create a QLabel instance
        self.verbose_checkbox = QCheckBox("High console verbosity")
        self.verbose_checkbox.setChecked(config.get("verbose", False))
        self.verbose_checkbox.setToolTip(
            "High level of verbosity in the console\n"
            "This includes a lot of internal logging\n"
            "from the langchain library.\n"
            "Nearly incomprehensible, but usefull\n"
            "if you are interested to see the prompts\n"
            "in action..."
        )
        # Add the install_missing_packages checkbox to the layout:
        self.layout.addWidget(self.verbose_checkbox)

    def _start_omega_button(self):
        aprint("Setting up start Omega button UI.")

        # Start Omega button:
        self.start_omega_button = QPushButton("Start Conversing with Omega")
        self.start_omega_button.clicked.connect(self._start_omega)
        self.start_omega_button.setToolTip(
            "Start Omega, this will open a browser window.\n"
            "You can restart Omega with new settings by\n"
            "clicking again this button. This closes the\n"
            "previous session."
        )
        # Omega button:
        self.layout.addWidget(self.start_omega_button)

    def _show_editor_button(self):
        aprint("Setting up open editor button UI.")

        # Start Omega button:
        self.show_editor_button = QPushButton("Show Omega's Code Editor")
        self.show_editor_button.clicked.connect(self._show_editor)
        self.show_editor_button.setToolTip(
            "Shows Omega's microplugin code snippet editor. \n"
            "All code generated by Omega is added to the editor\n"
            "so you can conveniently find it again after restarting\n"
            "napari, edit the code, reformat it, check for 'safety',\n"
            "send it to colleagues across the local network, and\n"
            "rerun the code. Running code for widgets adds the widget\n"
            "back to the viewer.\n"
        )
        # Omega button:
        self.layout.addWidget(self.show_editor_button)

    def _start_omega(self):
        try:
            with asection("Starting Omega now!"):

                # First we show the Omega's disclaimer that explains that
                # Omega is research software that can make changes to your data
                # and machine if instructed to do so or if it misunderstands the
                # requests.
                show_one_time_disclaimer_dialog(
                    "Omega is research software that can make changes to your data "
                    "and machine if instructed to do so or if it misunderstands "
                    "your requests. It is not perfect and can make mistakes. "
                    "By clicking 'I agree' you acknowledge that you understand "
                    "the potential dangers and agree to use Omega at your own risk. "
                    "You can find more information about Omega's disclaimer "
                    "and terms of use at <a href='https://github.com/royerlab/napari-chatgpt?tab=readme-ov-file#disclaimer' >disclaimer</a>."
                )

                # Stop previous instance if it exists:
                if self.server:
                    aprint("Server already started")
                    self.server.stop()

                # Temperature:
                temperature = float(
                    _creativity_mapping[self.creativity_combo_box.currentText()]
                )
                tool_temperature = 0.01 * temperature

                # Main model selection:
                main_llm_model_name = self.main_model_combo_box.currentText()

                # Set tool LLM model name via configuration file.
                tool_llm_model_name = self.tool_model_combo_box.currentText()

                aprint("Starting Omega Chat Server.")
                from napari_chatgpt.chat_server.chat_server import start_chat_server

                self.server = start_chat_server(
                    self.viewer,
                    main_llm_model_name=main_llm_model_name,
                    tool_llm_model_name=tool_llm_model_name,
                    temperature=temperature,
                    tool_temperature=tool_temperature,
                    has_builtin_websearch_tool=self.builtin_websearch_tool_checkbox.isChecked(),
                    memory_type="standard",
                    agent_personality=self.agent_personality_combo_box.currentText(),
                    fix_imports=self.fix_imports_checkbox.isChecked(),
                    install_missing_packages=self.install_missing_packages_checkbox.isChecked(),
                    fix_bad_calls=self.fix_bad_calls_checkbox.isChecked(),
                    autofix_mistakes=self.autofix_mistakes_checkbox.isChecked(),
                    autofix_widget=self.autofix_widgets_checkbox.isChecked(),
                    be_didactic=self.tutorial_mode_checkbox.isChecked(),
                    save_chats_as_notebooks=self.save_chats_as_notebooks.isChecked(),
                    verbose=self.verbose_checkbox.isChecked(),
                )

        except Exception as e:
            aprint(f"Error: {e}")
            aprint(
                "Omega failed to start. Please check the console for more information."
            )
            traceback.print_exc()

    def _show_editor(self):
        try:
            if not self.micro_plugin_main_window:
                aprint("MicroPluginMainWindow not instantiated.")
                return

            with asection("Showing editor now!"):

                # Set LLM parameters to self.micro_plugin_main_window:
                self.micro_plugin_main_window.code_editor_widget.llm_model_name = (
                    self.main_model_combo_box.currentText()
                )

                # Show the editor:
                self.micro_plugin_main_window.show()

                # Make sure to bring the window to the front:
                self.micro_plugin_main_window.raise_()

        except Exception as e:
            aprint(f"Error: {e}")
            aprint(
                "Omega failed to start. Please check the console for more information."
            )
            traceback.print_exc()

    def setStyleSheet(self, style):

        # Set the stylesheet for the micro plugin main window:
        if self.micro_plugin_main_window:
            self.micro_plugin_main_window.setStyleSheet(style)

        # Call the parent class method:
        super().setStyleSheet(style)

    def close(self):

        if self.server:
            self.server.stop()

        if self.micro_plugin_main_window:
            self.micro_plugin_main_window.hide()
            self.micro_plugin_main_window.close()

        super().close()


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
