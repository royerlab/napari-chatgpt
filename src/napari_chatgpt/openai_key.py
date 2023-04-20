from napari_chatgpt.utils.api_key_vault_dialog import \
    request_if_needed_api_key_dialog
import os

def set_openai_key():

    # Get the key from vault or via user, password protected:
    api_key = request_if_needed_api_key_dialog('OpenAI')

    # API KEY:
    os.environ['OPENAI_API_KEY'] = api_key
