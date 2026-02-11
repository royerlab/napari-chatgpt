"""Map OpenAI model names to their maximum context-window token limits."""


def openai_max_token_limit(llm_model_name):
    """Return the maximum token limit for a given OpenAI model name.

    Args:
        llm_model_name: The OpenAI model identifier string.

    Returns:
        Maximum number of tokens the model supports.
    """
    if (
        "gpt-4-1106-preview" in llm_model_name
        or "gpt-4-0125-preview" in llm_model_name
        or "gpt-4-vision-preview" in llm_model_name
    ):
        max_token_limit = 128000
    elif "32k" in llm_model_name:
        max_token_limit = 32000
    elif "16k" in llm_model_name:
        max_token_limit = 16385
    elif "gpt-4" in llm_model_name:
        max_token_limit = 8192
    elif "gpt-3.5-turbo-1106" in llm_model_name:
        max_token_limit = 16385
    elif "gpt-3.5" in llm_model_name:
        max_token_limit = 4096
    else:
        max_token_limit = 4096
    return max_token_limit
