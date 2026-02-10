__version__ = "2026.2.9"

import sys

if sys.platform == "win32":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")


def __getattr__(name: str):
    if name == "OmegaQWidget":
        from ._widget import OmegaQWidget

        return OmegaQWidget
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ("OmegaQWidget",)
