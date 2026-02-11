"""Utilities for loading LLM provider API keys into environment variables.

Maps friendly provider names (``"OpenAI"``, ``"Anthropic"``, ``"Gemini"``)
to their corresponding environment variable names and retrieves keys from
the encrypted vault when they are not already set.
"""

import os

from arbol import aprint, asection

from napari_chatgpt.utils.qt.qt_app import get_or_create_qt_app

__api_key_names = {}
__api_key_names["OpenAI"] = "OPENAI_API_KEY"
__api_key_names["Anthropic"] = "ANTHROPIC_API_KEY"
__api_key_names["Gemini"] = "GOOGLE_GEMINI_API_KEY"


def set_api_key(api_name: str) -> bool:
    """Load an API key into the environment, prompting the user if needed.

    If the key is not already present as an environment variable, opens
    the encrypted-vault Qt dialog to retrieve or create it.

    Args:
        api_name: Provider name (e.g. ``"OpenAI"``).

    Returns:
        True if the key is now set in ``os.environ``, False otherwise.
    """

    with asection(f"Setting API key: '{api_name}': "):

        # Api key name:
        api_key_name = __api_key_names[api_name]
        aprint(f"API key name: '{api_key_name}'")

        # If key is already present, no need to do anything:
        if is_api_key_available(api_name):
            aprint(f"API key is already set as an environment variable!")
            return True

        # Something technical required for Qt to be happy:
        app = get_or_create_qt_app()

        api_key = None
        if app:
            # Get the key from vault or via user, password protected:
            from napari_chatgpt.llm.api_keys.api_key_vault_dialog import (
                request_if_needed_api_key_dialog,
            )

            aprint(f"Requesting key from user via user interface...")
            api_key = request_if_needed_api_key_dialog(api_name)

        # Potentially releases the Qt app, MUST BE KEPT!:
        app = None

        # API KEY:
        if api_key:
            os.environ[api_key_name] = api_key
            return True
        else:
            return False


def is_api_key_available(api_name: str) -> bool:
    """Check whether the API key for the given provider is already set.

    Args:
        api_name: Provider name (e.g. ``"OpenAI"``).

    Returns:
        True if the corresponding environment variable is set.
    """
    # Api key name:
    api_key_name = __api_key_names[api_name]

    # Check if API key is set:
    return api_key_name in dict(os.environ)
