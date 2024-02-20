import sys
import tempfile
import traceback

from qtpy.QtWidgets import QApplication

from microplugin.microplugin_window import MicroPluginMainWindow


def myExceptionHook(exctype, value, tb):
    traceback.print_exception(exctype, value, tb)
    # You can also log to a file here or show a dialog to the user


# Override the default excepthook with our custom function
sys.excepthook = myExceptionHook

# Enable garbage collection debugging:
#gc.set_debug(gc.DEBUG_LEAK)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # temp folder as obtained with tempfile.TemporaryDirectory() in the main script:
    temp_folder = tempfile.TemporaryDirectory()

    # Turn off the singleton pattern:
    MicroPluginMainWindow._singleton_pattern_active = False

    # Instantiate the MicroPluginMainWindow:
    mainWindow = MicroPluginMainWindow(napari_viewer=None,
                                       folder_path=temp_folder.name)

    # Show the MicroPluginMainWindow:
    mainWindow.show()

    sys.exit(app.exec_())
