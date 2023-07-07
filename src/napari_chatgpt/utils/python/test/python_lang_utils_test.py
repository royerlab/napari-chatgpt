from pprint import pprint

from arbol import aprint

from napari_chatgpt.utils.python.python_lang_utils import enumerate_methods, \
    find_function_info_in_package, \
    get_function_info, object_info_str, extract_fully_qualified_function_names, \
    function_exists, get_imported_modules, get_function_signature


def test_object_info():
    string = 'string'
    info = object_info_str(string)
    pprint(info)
    assert "Class <class 'str'>" in info


def test_enumerate_methods():
    a_string = 'string'
    methods = list(enumerate_methods(a_string))
    pprint(methods)
    assert len(methods) > 0
    assert 'capitalize' in methods[0]


def test_find_functions_in_package():
    convolve_functions = list(
        find_function_info_in_package('scipy', 'convolve'))
    pprint(convolve_functions)

    assert 'scipy.ndimage.convolve' in convolve_functions
    assert 'scipy.signal.signaltools.convolve' in convolve_functions


def test_find_functions_in_package():
    signature = get_function_info('scipy.ndimage.convolve')
    pprint(signature)

    assert 'scipy.ndimage.convolve' in signature


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
    function_names, _ = extract_fully_qualified_function_names(code,
                                                               unzip_result=True)

    print('\n')
    for function_call in function_names:
        print(function_call)

    assert 'skimage.feature.canny' in function_names
    assert 'skimage.transform.probabilistic_hough_line' in function_names
    assert 'numpy.zeros_like' in function_names
    assert 'numpy.array' in function_names
    assert 'skimage.transform.line' in function_names


def test_function_exists():
    function_calls, _ = extract_fully_qualified_function_names(code,
                                                               unzip_result=True)

    print('\n')
    for function_call in function_calls:
        if function_exists(function_call):
            print(function_call, "exists!")
        else:
            print(function_call, "does not exist!")

    assert function_exists('skimage.feature.canny')
    assert function_exists('skimage.transform.probabilistic_hough_line')
    assert function_exists('numpy.zeros_like')
    assert function_exists('numpy.array')
    assert not function_exists('skimage.transform.line')


def test_get_imported_modules():
    modules = get_imported_modules(code)

    print('\n')
    pprint(modules)

    assert 'magicgui' in modules
    assert 'napari.types' in modules
    assert 'numpy' in modules
    assert 'skimage' in modules

# def test_find_functions_with_name():
#
#     print('\n')
#     modules = get_imported_modules(code)
#
#     functions = find_functions_with_name(modules, 'probabilistic_hough_line')
#
#     print('\n\n')
#     pprint(functions)

def test_get_function_signature():

    print('\n')

    signature = get_function_signature('napari_chatgpt.utils.python.python_lang_utils.get_function_signature')
    aprint(signature)
    assert 'get_function_signature(function_name: str, include_docstring: bool = False) -> str' in signature

    print('\n\n')

    signature = get_function_signature('numpy.zeros_like', include_docstring=True)
    aprint(signature)
    assert 'zeros_like(a, dtype, order, subok, shape)' in signature
    assert 'shape : int or sequence of ints, optional.' in signature

    print('\n\n')

    signature = get_function_signature('skimage.draw.line', include_docstring=True)
    aprint(signature)
    assert 'line(r0, c0, r1, c1)' in signature

    print('\n\n')

    signature = get_function_signature('skimage.transform.probabilistic_hough_line', include_docstring=True)
    aprint(signature)
    assert 'probabilistic_hough_line(image, threshold, line_length, line_gap, theta' in signature

    print('\n\n')







