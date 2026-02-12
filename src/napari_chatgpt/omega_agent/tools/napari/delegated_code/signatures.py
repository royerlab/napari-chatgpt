"""Function signature strings for the segmentation backends.

These string constants contain the function signatures (without bodies) for
``cellpose_segmentation``, ``stardist_segmentation``, and
``classic_segmentation``.  They are injected into the LLM prompt by
``CellNucleiSegmentationTool`` so the sub-LLM knows which functions are
available and how to call them.
"""

cellpose_signature = """
# Cellpose uses deep learning for cell/cytoplasm segmentation. Handles 2D and 3D.
def cellpose_segmentation( image: ArrayLike,
                           model_type: str = 'cyto',
                           normalize: Optional[bool] = True,
                           norm_range_low: Optional[float] = 1.0,
                           norm_range_high: Optional[float] = 99.8,
                           min_segment_size: int = 32,
                           channel: Optional[Sequence[int]] = None,
                           diameter: Optional[float] = None) -> ArrayLike
"""

stardist_signature = """
# StarDist uses deep learning for nuclei detection. Handles 2D and 3D (3D is done slice-by-slice with a 2D model).
# Valid model_type values: 'versatile_fluo', 'versatile_he', 'paper_dsb2018', 'demo' (do NOT use 3D model names).
def stardist_segmentation(image: ArrayLike,
                          model_type: str = 'versatile_fluo',
                          normalize: Optional[bool] = True,
                          norm_range_low: Optional[float] = 1.0,
                          norm_range_high: Optional[float] = 99.8,
                          min_segment_size: int = 32,
                          scale:float = None) -> ArrayLike
"""

classic_signature = """
# Classic segmentation supports multiple thresholding methods (Otsu, Li, Triangle, Yen, Isodata, Mean, Minimum). Fast, no GPU needed. Works in 2D, 3D, and higher dimensions.
def classic_segmentation(image: ArrayLike,
                          threshold_type: str = 'otsu',
                          normalize: Optional[bool] = True,
                          norm_range_low: Optional[float] = 1.0,
                          norm_range_high: Optional[float] = 99.8,
                          min_segment_size: int = 32,
                          erosion_steps: int = 1,
                          closing_steps: int = 1,
                          opening_steps: int = 0,
                          apply_watershed: bool = False,
                          min_distance: int = 15) -> ArrayLike
"""
