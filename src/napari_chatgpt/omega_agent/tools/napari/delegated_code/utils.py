# Function that checks if the packages stardist or napari-stardist are installed:
from arbol import aprint


def check_stardist_installed() -> bool:
    """
    Check if the StarDist package is installed.
    
    Returns:
        bool: True if StarDist is available, False otherwise.
    """
    try:
        import stardist

        return True
    except ImportError:
        return False


# Function that checks if the packages cellpose or cellpose-napari are installed:
def check_cellpose_installed() -> bool:
    """
    Check if the Cellpose package is installed.
    
    Returns:
        bool: True if Cellpose is available, False otherwise.
    """
    try:
        import cellpose

        return True
    except ImportError:
        return False


def get_list_of_algorithms() -> str:
    """
    Return a list of available image segmentation algorithms based on installed packages.
    
    Returns:
        algos (list of str): Names of segmentation algorithms available for use, such as "cellpose", "stardist", and "classic".
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
    """
    Generate a descriptive summary of available image segmentation algorithms and their recommended use cases.
    
    Returns:
        str: A string describing example requests for each available segmentation algorithm and guidance on when to use each one.
    """
    description = ""

    algos = get_list_of_algorithms()

    description += "For example, you can request to: "

    for algo in algos:
        if "cellpose" in algo:
            description += "'segment cell's cytoplams in given layer with Cellpose', "

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
            description += (
                "Classic for very contrasted and easy to segment 2D or 3D images, "
            )

    # remove last comma:
    description = description[:-2]

    description += ". "

    return description
