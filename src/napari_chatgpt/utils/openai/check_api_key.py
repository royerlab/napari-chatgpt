from arbol import aprint


def check_openai_api_key(openai_api_key: str) -> bool:
    """
    Validate an OpenAI API key by attempting a test request.
    
    Parameters:
        openai_api_key (str): The API key to validate.
    
    Returns:
        bool: True if the API key is valid, False if invalid.
    """

    import openai

    # Save existing API key:
    existing_api_key = openai.api_key

    try:
        # Tries to use the API key:
        import openai

        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test message"}],
        )
        aprint("API key is valid.")
        return True

    except openai.error.AuthenticationError:
        aprint("Invalid API key.")
        return False

    finally:
        # Restore existing API key:
        if existing_api_key:
            openai.api_key = existing_api_key
