
cellpose_signature = """
# Cellpose is better for segmenting non-convex cells, in particular their cytoplasm, it is a deep learning based method that only work in 2D and are better for small images. 
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
# StarDist is better for segmenting nearly convex nuclei, it is a deep learning based method that only work in 2D and are better for small images. 
def stardist_segmentation(image: ArrayLike,
                          model_type: str = '2D_versatile_fluo',
                          normalize: Optional[bool] = True,
                          norm_range_low: Optional[float] = 1.0,
                          norm_range_high: Optional[float] = 99.8,
                          min_segment_size: int = 32,
                          scale:float = None) -> ArrayLike
"""

classic_signature = """
# Classic segmentation is a simple thresholding method that can be used as a baseline and works in 2D, 3D and more dimensions.
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
                          min_distance: int = 10) -> ArrayLike
```
"""