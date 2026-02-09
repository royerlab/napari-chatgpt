"""Sample data for napari-chatgpt (Omega)."""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

LayerDataTuple = Tuple[np.ndarray, dict, str]


def make_sample_data() -> List[LayerDataTuple]:
    """Return a human mitosis image as sample data.

    Fallback chain: human_mitosis -> cells3d membrane channel -> synthetic.
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
