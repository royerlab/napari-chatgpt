from napari_chatgpt.utils.python.python_lang_utils import (
    enumerate_methods, extract_fully_qualified_function_names,
    find_function_info_in_package, function_exists, get_function_info,
    get_function_signature, get_imported_modules, object_info_str)


def test_object_info():
    string = "string"
    info = object_info_str(string)
    assert "Class <class 'str'>" in info


def test_enumerate_methods():
    a_string = "string"
    methods = list(enumerate_methods(a_string))
    assert len(methods) > 0
    assert "capitalize" in methods[0]


def test_find_functions_in_package():
    convolve_functions = list(find_function_info_in_package("scipy", "convolve"))

    assert any("scipy.ndimage.convolve" in f for f in convolve_functions)
    assert any("scipy.signal" in f and "convolve" in f for f in convolve_functions)


def test_get_function_info():
    signature = get_function_info("scipy.ndimage.convolve")
    assert "scipy.ndimage.convolve" in signature


code = """
import numpy as np
from skimage import feature, transform
from napari.types import ImageData, LabelsData
from magicgui import magicgui

@magicgui(call_button='Find Straight Lines')
def find_straight_lines(image: ImageData) -> LabelsData:
    edges = feature.canny(image)
    hough_lines = transform.probabilistic_hough_line(edges)

    labels = np.zeros_like(image, dtype=np.uint32)
    label_counter = 1

    for line in hough_lines:
        (x1, y1), (x2, y2) = line
        rr, cc = np.array(transform.line(x1, y1, x2, y2))
        labels[rr, cc] = label_counter
        label_counter += 1

    return labels
"""


def test_extract_function_calls():
    function_names, _ = extract_fully_qualified_function_names(code, unzip_result=True)

    assert "skimage.feature.canny" in function_names
    assert "skimage.transform.probabilistic_hough_line" in function_names
    assert "numpy.zeros_like" in function_names
    assert "numpy.array" in function_names
    assert "skimage.transform.line" in function_names


def test_function_exists():
    function_calls, _ = extract_fully_qualified_function_names(code, unzip_result=True)

    assert function_exists("skimage.feature.canny")
    assert function_exists("skimage.transform.probabilistic_hough_line")
    assert function_exists("numpy.zeros_like")
    assert function_exists("numpy.array")
    assert not function_exists("skimage.transform.line")


def test_get_imported_modules():
    modules = get_imported_modules(code)

    assert "magicgui" in modules
    assert "napari.types" in modules
    assert "numpy" in modules
    assert "skimage" in modules


def test_get_function_signature():
    signature = get_function_signature(
        "napari_chatgpt.utils.python.python_lang_utils.get_function_signature"
    )
    assert (
        "get_function_signature(function_name: str, include_docstring: bool = False) -> str"
        in signature
    )

    signature = get_function_signature("numpy.zeros_like", include_docstring=True)
    assert (
        "zeros_like(a, dtype, order, subok, shape, device)" in signature
        or "zeros_like(a, dtype, order, subok, shape)" in signature
    )
    assert "shape : int or sequence of ints, optional." in signature

    signature = get_function_signature("skimage.draw.line", include_docstring=True)
    assert "line(r0, c0, r1, c1)" in signature

    signature = get_function_signature(
        "skimage.transform.probabilistic_hough_line", include_docstring=True
    )
    assert (
        "probabilistic_hough_line(image, threshold, line_length, line_gap, theta"
        in signature
    )
