from arbol import aprint


def check_openai_api_key(openai_api_key: str) -> bool:
    """
    Check if the OpenAI API key is valid.

    Args:
    api_key (
    """

    import openai

    # Save existing API key:
    existing_api_key = openai.api_key

    try:
        # Tries to use the API key:
        import openai

        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test message"}]
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