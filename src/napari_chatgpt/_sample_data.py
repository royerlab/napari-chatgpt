"""Sample data provider for the napari-chatgpt plugin.

Registered as a napari sample-data contribution so users can quickly load
a test image via *File > Open Sample > napari-chatgpt*.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

LayerDataTuple = Tuple[np.ndarray, dict, str]
"""Type alias for a single napari layer-data tuple ``(data, kwargs, type)``."""


def make_sample_data() -> List[LayerDataTuple]:
    """Return a human-mitosis image as napari sample data.

    Uses a fallback chain so the function never fails:

    1. ``skimage.data.human_mitosis`` (preferred).
    2. ``skimage.data.cells3d`` membrane channel.
    3. Random 256x256 uint8 noise (last resort).

    Returns:
        A single-element list containing a ``(data, metadata, layer_type)``
        tuple suitable for ``napari.Viewer.open_sample()``.
    """
    try:
        from skimage.data import human_mitosis

        image = human_mitosis()
    except Exception:
        try:
            from skimage.data import cells3d

            image = cells3d()[:, 1, :, :]  # membrane channel
        except Exception:
            image = np.random.default_rng(42).integers(
                0, 255, (256, 256), dtype=np.uint8
            )

    return [(image, {"name": "Human Mitosis (Omega sample)"}, "image")]
