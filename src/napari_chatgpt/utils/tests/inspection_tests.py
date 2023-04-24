from pprint import pprint

from arbol import aprint
from napari import viewer

from src.napari_chatgpt.utils.inspection import enumerate_methods, \
    find_function_info_in_package, \
    get_function_info, object_info_str


def test_object_info():
    n_viewer = viewer.Viewer()
    info = object_info_str(n_viewer)
    aprint(info)


def test_enumerate_methods():
    n_viewer = viewer.Viewer()
    methods = list(enumerate_methods(n_viewer))
    pprint(methods)

    a_string = 'string'
    methods = list(enumerate_methods(a_string))
    pprint(methods)


def test_find_functions_in_package():
    convolve_functions = list(
        find_function_info_in_package('scipy', 'convolve'))
    pprint(convolve_functions)


def test_find_functions_in_package():
    signature = get_function_info('scipy.ndimage.convolve')
    pprint(signature)
