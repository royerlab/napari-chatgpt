"""Utility functions for detecting installed segmentation backends.

Provides helpers to check whether Cellpose and StarDist are importable,
and to build human-readable lists and descriptions of available
segmentation algorithms for use in LLM prompts and tool descriptions.
"""

from arbol import aprint


def check_stardist_installed() -> bool:
    """Return True if the ``stardist`` package is importable."""
    try:
        import stardist  # noqa: F401

        return True
    except ImportError:
        return False


def check_cellpose_installed() -> bool:
    """Return True if the ``cellpose`` package is importable."""
    try:
        import cellpose  # noqa: F401

        return True
    except ImportError:
        return False


def get_list_of_algorithms() -> list:
    """Return the names of available segmentation algorithms.

    Always includes ``"classic"``; conditionally includes ``"cellpose"``
    and ``"stardist"`` if their packages are installed.

    Returns:
        A list of algorithm name strings.
    """
    algos = []
    if check_cellpose_installed():
        aprint("Cellpose is installed!")
        algos.append("cellpose")
    if check_stardist_installed():
        aprint("Stardist is installed!")
        algos.append("stardist")

    algos.append("classic")
    return algos


def get_description_of_algorithms() -> str:
    """Build a human-readable description of available segmentation algorithms.

    Generates example usage strings and guidance on when to choose each
    algorithm.  Used in the ``CellNucleiSegmentationTool`` description.

    Returns:
        A formatted description string.
    """
    description = ""

    algos = get_list_of_algorithms()

    description += "For example, you can request to: "

    for algo in algos:
        if "cellpose" in algo:
            description += "'segment cell's cytoplasms in given layer with Cellpose', "

        elif "stardist" in algo:
            description += "'segment cell nuclei in selected 3D layer with StarDist', "

        elif "classic" in algo:
            description += (
                "'segment cell nuclei in 3D layer named 'some_name' with Classic', "
            )

    # remove last comma:
    description = description[:-2]

    description += ". Choose: "

    for algo in algos:
        if "cellpose" in algo:
            description += "Cellpose for segmenting irregular or non-convex cytoplasms or membrane outlines in 2D, "

        elif "stardist" in algo:
            description += "StarDist for segmenting near-convex nuclei in 2D or 3D, "

        elif "classic" in algo:
            description += "Classic for threshold-based segmentation (Otsu, Li, Triangle, Yen, etc.) in 2D/3D — fast, no GPU required, "

    # remove last comma:
    description = description[:-2]

    description += ". "

    return description
