"""Validate an OpenAI API key by making a lightweight API call."""

from arbol import aprint


def check_openai_api_key(openai_api_key: str) -> bool:
    """
    Check if the OpenAI API key is valid.

    Parameters
    ----------
    openai_api_key : str
        The OpenAI API key to check.

    Returns
    -------
    bool
        True if the API key is valid, False otherwise.
    """
    try:
        from openai import AuthenticationError, OpenAI

        # Create a client with the provided API key:
        client = OpenAI(api_key=openai_api_key)

        # Try a minimal API call to validate the key:
        client.models.list()

        aprint("API key is valid.")
        return True

    except AuthenticationError:
        aprint("Invalid API key.")
        return False

    except Exception as e:
        aprint(f"Error checking API key: {e}")
        return False
