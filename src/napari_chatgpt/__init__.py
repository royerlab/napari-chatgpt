"""napari-chatgpt: LLM-powered autonomous agent plugin for napari.

Provides **Omega**, a conversational AI assistant that performs interactive
image processing and analysis inside the napari viewer.  Multiple LLM
backends (OpenAI, Anthropic, Gemini) are supported via the LiteMind library.

The main entry point is :class:`OmegaQWidget`, lazily imported to keep
startup lightweight.
"""

__version__ = "2026.2.9"

import sys

if sys.platform == "win32":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")


def __getattr__(name: str):
    """Lazily import heavy dependencies to keep ``import napari_chatgpt`` fast."""
    if name == "OmegaQWidget":
        from ._widget import OmegaQWidget

        return OmegaQWidget
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ("OmegaQWidget",)
