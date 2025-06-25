from arbol import asection


def get_anthropic_model_list() -> list[str]:
    """
    Return a list of all *current, non-deprecated* Anthropic Claude models.

    Snapshot dates ensure deterministic behaviour.  Last verified: 2025-06-25.
    """
    with asection("Enumerating active Anthropic models"):
        return [
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20240620",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-7-sonnet-20250219",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
        ]
