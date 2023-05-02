import os
import sys

from PyQt5.QtWidgets import QApplication

from napari_chatgpt.utils.api_key_vault_dialog import \
    request_if_needed_api_key_dialog


def set_openai_key() -> bool:
    # If key is already present, no need to do anthing:
    if is_openai_key_available():
        return True

    # Check if there is already a QApplication instance running
    if not QApplication.instance():
        # If not, create a new QApplication instance
        app = QApplication(sys.argv)
    else:
        # If there is, use the existing QApplication instance
        app = QApplication.instance()

    # Get the key from vault or via user, password protected:
    api_key = request_if_needed_api_key_dialog('OpenAI')

    # API KEY:
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
    else:
        return False

def is_openai_key_available() -> bool:
    return 'OPENAI_API_KEY' in dict(os.environ)