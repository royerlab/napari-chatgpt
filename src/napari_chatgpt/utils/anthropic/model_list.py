"""Utilities for retrieving the list of available Anthropic Claude models."""

from arbol import asection


def get_anthropic_model_list() -> list[str]:
    """
    Return a list of all *current, non-deprecated* Anthropic Claude models.

    Snapshot dates ensure deterministic behaviour.  Last verified: 2026-02-07.
    """
    with asection("Enumerating active Anthropic models"):
        return [
            # Current (recommended):
            "claude-opus-4-6",
            "claude-sonnet-4-5-20250929",
            "claude-haiku-4-5-20251001",
            # Legacy (still available):
            "claude-opus-4-5-20251101",
            "claude-opus-4-1-20250805",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-3-7-sonnet-20250219",
            "claude-3-haiku-20240307",
        ]
