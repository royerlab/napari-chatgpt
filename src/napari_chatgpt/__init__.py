try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
from ._widget import OmegaQWidget

__all__ = (
    "OmegaQWidget"
)
